from __future__ import annotations

import asyncio
import logging
from typing import Protocol

from langchain_components.runtime.context import RuntimeContext
from langchain_components.runtime.events import RuntimeEvent
from langchain_components.runtime.exceptions import (
    ExecutionError,
    PlanningError,
    ReflectionError,
    StepExecutionError,
)
from langchain_components.runtime.executor import RuntimeExecutor
from langchain_components.memory.runtime.manager import MemoryManager
from langchain_components.runtime.models import ExecutionResult, RuntimeResult, RuntimeStep
from langchain_components.runtime.reflection import ReflectionEngine
from langchain_components.runtime.reflection_models import ReflectionAction, ReflectionDecision
from langchain_components.runtime.state import RuntimeState
from langchain_components.tools.schemas import ToolResult

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 2



class BaseAgent(Protocol):
    name: str
    planner: object
    tool_executor: object


class AgentRuntime:
    def __init__(
        self,
        executor: RuntimeExecutor | None = None,
        memory: MemoryManager | None = None,
        reflection: ReflectionEngine | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        
        self._executor = executor or RuntimeExecutor()
        self._memory = memory or MemoryManager()
        self._reflection = reflection or ReflectionEngine()
        self._max_retries = max_retries

    def execute(self, agent: BaseAgent, state: RuntimeState) -> RuntimeResult:
        
        return asyncio.run(self.execute_async(agent, state))

    async def execute_async(self, agent: BaseAgent, state: RuntimeState) -> RuntimeResult:
        context = RuntimeContext(
            state=state,
            planner=agent.planner,
            executor=self._executor,
            tool_executor=agent.tool_executor,
            memory_manager=self._memory,
            agent_name=agent.name,
        )
        logger.info("runtime started agent=%s session=%s", agent.name, state.session_id)

        self._load_memory(context)

        self._plan(context)
        result, decision = await self._run_control_loop(context)

        self._save_memory(context)
        final = self._finalize(context, result, decision)

        logger.info("runtime finished agent=%s session=%s", agent.name, state.session_id)
        return final

    def _load_memory(self, context: RuntimeContext) -> None:
        logger.info("memory load started")
        self._memory.load(context.state)
        logger.info("memory load finished")

    def _save_memory(self, context: RuntimeContext) -> None:
        logger.info("memory save started")
        self._memory.save(context.state)
        logger.info("memory save finished")

    def _plan(self, context: RuntimeContext) -> list[RuntimeStep]:
        logger.info("planning started")
        try:
            plan = context.planner.create_plan(context.state)
        except Exception as exc:
            raise PlanningError(str(exc)) from exc
        context.state.plan = plan
        logger.info("planning finished steps=%d", len(plan))
        return plan

    async def _run_control_loop(
        self, context: RuntimeContext
    ) -> tuple[ExecutionResult, ReflectionDecision]:
        """Executes the plan one step at a time, reflecting after every
        step and acting on the decision before touching the next one."""
        completed_steps: list[str] = []
        tool_results: list[ToolResult] = []
        events: list[RuntimeEvent] = []
        retry_counts: dict[str, int] = {}

        if not context.state.plan:
            # nothing to do — vacuously complete
            decision = ReflectionDecision(action=ReflectionAction.COMPLETE, reason="Empty plan.")
            return self._accumulated_result(completed_steps, tool_results, events, None), decision

        for step in context.state.plan:
            if step.completed:
                continue

            while True:
                tool_result, step_events = await self._execute_one_step(context, step)
                events.extend(step_events)
                if tool_result is not None:
                    tool_results.append(tool_result)

                step_result = self._step_result(step, tool_result)
                decision = await self._reflect(context, step_result)
                decision = self._enforce_failure_invariants(step, tool_result, decision)

                if decision.action == ReflectionAction.RETRY:
                    attempt = retry_counts.get(step.name, 0)
                    if attempt < self._max_retries:
                        retry_counts[step.name] = attempt + 1
                        logger.info(
                            "retrying step=%s attempt=%d/%d", step.name, attempt + 1, self._max_retries
                        )
                        continue  # same step, again

                    logger.warning(
                        "step=%s exhausted retries (%d) — converting to terminal abort",
                        step.name, self._max_retries,
                    )
                    decision = ReflectionDecision(
                        action=ReflectionAction.ABORT,
                        reason=f"Step '{step.name}' failed after {self._max_retries} retries.",
                        source="runtime",
                    )
                    result = self._accumulated_result(completed_steps, tool_results, events, step.name)
                    return result, decision

                if decision.action == ReflectionAction.CONTINUE:
                    completed_steps.append(step.name)
                    break  # next step in the outer for-loop

                if decision.action == ReflectionAction.COMPLETE:
                    completed_steps.append(step.name)
                    result = self._accumulated_result(completed_steps, tool_results, events, None)
                    return result, decision

                # ASK_USER or ABORT — stop immediately, remaining steps untouched
                failed_step = step.name if not (tool_result and tool_result.success) else None
                result = self._accumulated_result(completed_steps, tool_results, events, failed_step)
                return result, decision

        # every step in the plan was already marked completed on entry
        # (e.g. a resumed multi-turn plan) — nothing new to reflect on
        decision = ReflectionDecision(action=ReflectionAction.COMPLETE, reason="All steps already completed.")
        return self._accumulated_result(completed_steps, tool_results, events, None), decision

    async def _execute_one_step(
        self, context: RuntimeContext, step: RuntimeStep
    ) -> tuple[ToolResult | None, list[RuntimeEvent]]:
        try:
            return await context.executor.execute_step(context, step)
        except StepExecutionError as exc:
           
            return None, exc.events
        except Exception as exc:
            raise ExecutionError(str(exc)) from exc

    @staticmethod
    def _enforce_failure_invariants(
        step: RuntimeStep, tool_result: ToolResult | None, decision: ReflectionDecision
    ) -> ReflectionDecision:
        
        tool_failed = not (tool_result and tool_result.success)

        if tool_failed and decision.action in (ReflectionAction.COMPLETE, ReflectionAction.CONTINUE):
            logger.error(
                "Reflection returned %s for a failed step '%s' — not permitted, "
                "overriding to ABORT. Original reason: %s",
                decision.action.value, step.name, decision.reason,
            )
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=(
                    f"Safety invariant violated: Reflection returned "
                    f"{decision.action.value} for a failed step ('{step.name}'), "
                    f"which is never allowed. Original reflection reason: {decision.reason}"
                ),
                source="runtime",
            )

        return decision

    @staticmethod
    def _step_result(step: RuntimeStep, tool_result: ToolResult | None) -> ExecutionResult:
        success = bool(tool_result and tool_result.success)
        return ExecutionResult(
            success=success,
            completed_steps=[step.name] if success else [],
            tool_results=[tool_result] if tool_result else [],
            failed_step=None if success else step.name,
        )

    @staticmethod
    def _accumulated_result(
        completed_steps: list[str],
        tool_results: list[ToolResult],
        events: list[RuntimeEvent],
        failed_step: str | None,
    ) -> ExecutionResult:
        return ExecutionResult(
            success=failed_step is None,
            completed_steps=completed_steps,
            tool_results=tool_results,
            runtime_events=events,
            failed_step=failed_step,
        )

    async def _reflect(self, context: RuntimeContext, result: ExecutionResult) -> ReflectionDecision:
        try:
            decision = await self._reflection.reflect(context, result)
        except Exception as exc:
            raise ReflectionError(str(exc)) from exc
        logger.info(
            "reflection action=%s source=%s reason=%s",
            decision.action.value, decision.source, decision.reason,
        )
        return decision

    def _finalize(
        self, context: RuntimeContext, result: ExecutionResult, decision: ReflectionDecision
    ) -> RuntimeResult:
        metadata = {
            "reflection_action": decision.action.value,
            "reflection_reason": decision.reason,
            "reflection_source": decision.source,
        }
        if result.failed_step:
            metadata["failed_step"] = result.failed_step
        if decision.ask_user_message:
            metadata["ask_user_message"] = decision.ask_user_message

        success = result.success and decision.action != ReflectionAction.ABORT

        return RuntimeResult(
            success=success,
            answer=self._extract_answer(result, decision),
            state=context.state.working_memory.variables,
            tool_calls=result.completed_steps,
            metadata=metadata,
        )

    def _extract_answer(self, result: ExecutionResult, decision: ReflectionDecision) -> str:
        if decision.action == ReflectionAction.ASK_USER and decision.ask_user_message:
            return decision.ask_user_message

        
        if not result.tool_results:
            return ""
        last = result.tool_results[-1]
        if isinstance(last.data, dict) and "answer" in last.data:
            return str(last.data["answer"])
        return ""