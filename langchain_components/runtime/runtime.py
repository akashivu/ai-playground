from __future__ import annotations

import asyncio
import copy
import logging
import time
from typing import Protocol

from langchain_components.runtime.checkpoint import CheckpointManager
from langchain_components.runtime.checkpoint_models import ExecutionCheckpoint, ExecutionStatus
from langchain_components.runtime.context import RuntimeContext
from langchain_components.runtime.events import RuntimeEvent
from langchain_components.runtime.exceptions import (
    CheckpointError,
    ExecutionError,
    PlanningError,
    ReflectionError,
    StepExecutionError,
)
from langchain_components.runtime.executor import RuntimeExecutor
from langchain_components.memory.runtime.manager import MemoryManager
from langchain_components.memory.runtime.models import WorkingMemory
from langchain_components.runtime.models import ExecutionResult, RuntimeResult, RuntimeStep
from langchain_components.runtime.reflection import ReflectionEngine
from langchain_components.runtime.reflection_models import ReflectionAction, ReflectionDecision
from langchain_components.runtime.state import RuntimeState
from langchain_components.tools.schemas import ToolResult

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 2


USER_RESPONSE_KEY = "user_response"


_ACTION_TO_STATUS = {
    ReflectionAction.RETRY: ExecutionStatus.RUNNING,
    ReflectionAction.CONTINUE: ExecutionStatus.RUNNING,
    ReflectionAction.COMPLETE: ExecutionStatus.COMPLETED,
    ReflectionAction.ASK_USER: ExecutionStatus.WAITING_FOR_USER,
    ReflectionAction.ABORT: ExecutionStatus.ABORTED,
}


# placeholder shape until this is swapped for the real
# langchain_components.agents.BaseAgent import
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
        checkpoint_manager: CheckpointManager | None = None,
        require_durable_checkpoints: bool = False,
    ):
        # execution engine, memory, and reflection all belong to the
        # runtime, not the agent
        self._executor = executor or RuntimeExecutor()
        self._memory = memory or MemoryManager()
        self._reflection = reflection or ReflectionEngine()
        self._max_retries = max_retries
        
        self._checkpoint_manager = checkpoint_manager
       
        self._require_durable_checkpoints = require_durable_checkpoints

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
            # fresh trace_id/execution_id every call — a new execution can
            # never collide with or accidentally resume an old checkpoint
        )
        logger.info(
            "runtime started agent=%s session=%s execution=%s",
            agent.name, state.session_id, context.trace_id,
        )

        self._load_memory(context)
        self._plan(context)

        created_at = time.time()
        result, decision, checkpoint_durable = await self._run_control_loop(
            context, created_at=created_at, resume_count=0
        )

        self._save_memory(context)
        final = self._finalize(context, result, decision, checkpoint_durable)

        logger.info(
            "runtime finished agent=%s session=%s execution=%s",
            agent.name, state.session_id, context.trace_id,
        )
        return final

    def resume(
        self,
        agent: BaseAgent,
        session_id: str,
        execution_id: str,
        user_input: str | None = None,
    ) -> RuntimeResult:
        """Sync wrapper for resume_async() — same asyncio.run() caveat as execute()."""
        return asyncio.run(self.resume_async(agent, session_id, execution_id, user_input))

    async def resume_async(
        self,
        agent: BaseAgent,
        session_id: str,
        execution_id: str,
        user_input: str | None = None,
    ) -> RuntimeResult:
        
        if self._checkpoint_manager is None:
            raise CheckpointError(
                "Checkpointing is not configured on this AgentRuntime — "
                "pass a checkpoint_manager to resume an execution."
            )

        # agent_name=agent.name: reject resuming a different agent's
        # execution even if session_id happens to match
        checkpoint = self._checkpoint_manager.restore(execution_id, session_id, agent_name=agent.name)

        state = RuntimeState(
            agent=checkpoint.agent,
            session_id=checkpoint.session_id,
            user_id=checkpoint.runtime_metadata.get("user_id", ""),
            query=checkpoint.runtime_metadata.get("query", ""),
            plan=[snapshot.to_runtime_step() for snapshot in checkpoint.plan_state],
        )

        context = RuntimeContext(
            state=state,
            planner=agent.planner,
            executor=self._executor,
            tool_executor=agent.tool_executor,
            memory_manager=self._memory,
            agent_name=agent.name,
            trace_id=execution_id,  # reuse — this IS the same execution, continuing
        )
        logger.info(
            "runtime resuming agent=%s session=%s execution=%s",
            agent.name, session_id, execution_id,
        )

        
        self._load_memory(context)
        context.state.working_memory = WorkingMemory(variables=dict(checkpoint.working_memory))

        if user_input is not None:
            self._apply_user_input(context, checkpoint, user_input)

        retry_counts = dict(checkpoint.retry_counts)
        created_at = checkpoint.created_at
        resume_count = checkpoint.resume_count + 1

        
        recorded = self._checkpoint(
            context, retry_counts, current_step=checkpoint.current_step,
            status=ExecutionStatus.RUNNING, created_at=created_at, resume_count=resume_count,
        )
        if not recorded and self._require_durable_checkpoints:
            raise CheckpointError(
                f"Failed to durably record resume for execution_id={execution_id!r} "
                f"and require_durable_checkpoints is enabled — refusing to proceed."
            )

        
        result, decision, checkpoint_durable = await self._run_control_loop(
            context, retry_counts=retry_counts, created_at=created_at, resume_count=resume_count,
        )

        self._save_memory(context)
        final = self._finalize(context, result, decision, checkpoint_durable)

        logger.info(
            "runtime resume finished agent=%s session=%s execution=%s",
            agent.name, session_id, execution_id,
        )
        return final

    @staticmethod
    def _apply_user_input(
        context: RuntimeContext, checkpoint: ExecutionCheckpoint, user_input: str
    ) -> None:
        # available generically to any subsequent step/tool logic
        context.state.working_memory.variables[USER_RESPONSE_KEY] = user_input

        
        target_step_name = checkpoint.current_step
        if target_step_name is None:
            return
        for step in context.state.plan:
            if step.name == target_step_name and not step.completed:
                step.payload = {**step.payload, USER_RESPONSE_KEY: user_input}
                break

    def _load_memory(self, context: RuntimeContext) -> None:
        logger.info(
            "memory load started execution=%s session=%s", context.trace_id, context.state.session_id
        )
        self._memory.load(context.state)
        logger.info(
            "memory load finished execution=%s session=%s", context.trace_id, context.state.session_id
        )

    def _save_memory(self, context: RuntimeContext) -> None:
        logger.info(
            "memory save started execution=%s session=%s", context.trace_id, context.state.session_id
        )
        self._memory.save(context.state)
        logger.info(
            "memory save finished execution=%s session=%s", context.trace_id, context.state.session_id
        )

    def _plan(self, context: RuntimeContext) -> list[RuntimeStep]:
        logger.info(
            "planning started execution=%s session=%s", context.trace_id, context.state.session_id
        )
        try:
            plan = context.planner.create_plan(context.state)
        except Exception as exc:
            raise PlanningError(str(exc)) from exc
        
        context.state.plan = copy.deepcopy(plan)
        logger.info(
            "planning finished execution=%s session=%s steps=%d",
            context.trace_id, context.state.session_id, len(context.state.plan),
        )
        return context.state.plan

    async def _run_control_loop(
        self,
        context: RuntimeContext,
        retry_counts: dict[str, int] | None = None,
        created_at: float | None = None,
        resume_count: int = 0,
    ) -> tuple[ExecutionResult, ReflectionDecision, bool]:
        
        completed_steps: list[str] = []
        tool_results: list[ToolResult] = []
        events: list[RuntimeEvent] = []
        retry_counts = retry_counts if retry_counts is not None else {}
        created_at = created_at if created_at is not None else time.time()
        checkpoint_durable = True

        if not context.state.plan:
            # nothing to do — vacuously complete
            decision = ReflectionDecision(action=ReflectionAction.COMPLETE, reason="Empty plan.")
            result = self._accumulated_result(completed_steps, tool_results, events, None)
            return result, decision, checkpoint_durable

        for step in context.state.plan:
            if step.completed:
                # already done in a prior attempt (resume) — never replayed
                completed_steps.append(step.name)
                continue

            while True:
                tool_result, step_events = await self._execute_one_step(context, step)
                events.extend(step_events)
                if tool_result is not None:
                    tool_results.append(tool_result)

                step_result = self._step_result(step, tool_result)
                decision = await self._reflect(context, step, step_result)
                decision = self._enforce_failure_invariants(context, step, tool_result, decision)
                decision = self._enforce_retry_step_invariant(context, step, decision)

                status = _ACTION_TO_STATUS.get(decision.action, ExecutionStatus.RUNNING)

                if decision.action == ReflectionAction.RETRY:
                    attempt = retry_counts.get(step.name, 0)
                    if attempt < self._max_retries:
                        retry_counts[step.name] = attempt + 1
                        logger.info(
                            "retrying execution=%s session=%s step=%s attempt=%d/%d",
                            context.trace_id, context.state.session_id,
                            step.name, attempt + 1, self._max_retries,
                        )
                    else:
                        logger.warning(
                            "execution=%s session=%s step=%s exhausted retries (%d) — "
                            "converting to terminal failure",
                            context.trace_id, context.state.session_id,
                            step.name, self._max_retries,
                        )
                        decision = ReflectionDecision(
                            action=ReflectionAction.ABORT,
                            reason=f"Step '{step.name}' failed after {self._max_retries} retries.",
                            source="runtime",
                        )
                        status = ExecutionStatus.FAILED

                checkpoint_ok = self._checkpoint(
                    context, retry_counts, current_step=step.name,
                    status=status, created_at=created_at, resume_count=resume_count,
                )
                if not checkpoint_ok:
                    checkpoint_durable = False
                    if self._require_durable_checkpoints:
                        logger.error(
                            "execution=%s session=%s step=%s: checkpoint durability required "
                            "but write failed — aborting rather than risk a stale checkpoint "
                            "being replayed later",
                            context.trace_id, context.state.session_id, step.name,
                        )
                        decision = ReflectionDecision(
                            action=ReflectionAction.ABORT,
                            reason=(
                                f"Checkpoint write failed for step '{step.name}' and "
                                f"require_durable_checkpoints is enabled — stopping rather "
                                f"than continue without a durable record of this step."
                            ),
                            source="runtime",
                        )
                        # note: this ABORT's own status is NOT re-checkpointed —
                        # the store just failed, so nothing new can be durably
                        # written to it right now, including this abort record

                if decision.action == ReflectionAction.RETRY:
                    continue  # same step, again

                if decision.action == ReflectionAction.CONTINUE:
                    completed_steps.append(step.name)
                    break  # next step in the outer for-loop

                if decision.action == ReflectionAction.COMPLETE:
                    completed_steps.append(step.name)
                    result = self._accumulated_result(completed_steps, tool_results, events, None)
                    return result, decision, checkpoint_durable

                # ASK_USER or ABORT — stop immediately, remaining steps untouched
                failed_step = step.name if not (tool_result and tool_result.success) else None
                result = self._accumulated_result(completed_steps, tool_results, events, failed_step)
                return result, decision, checkpoint_durable

        # every step in the plan was already marked completed on entry
        # (e.g. a resumed plan where everything had already finished)
        decision = ReflectionDecision(action=ReflectionAction.COMPLETE, reason="All steps already completed.")
        result = self._accumulated_result(completed_steps, tool_results, events, None)
        return result, decision, checkpoint_durable

    async def _execute_one_step(
        self, context: RuntimeContext, step: RuntimeStep
    ) -> tuple[ToolResult | None, list[RuntimeEvent]]:
        try:
            return await context.executor.execute_step(context, step)
        except StepExecutionError as exc:
            # tool wasn't registered — no ToolResult exists, Reflection
            # handles this via its own "no result produced" ABORT path
            return None, exc.events
        except Exception as exc:
            raise ExecutionError(str(exc)) from exc

    def _checkpoint(
        self,
        context: RuntimeContext,
        retry_counts: dict[str, int],
        current_step: str | None,
        status: ExecutionStatus,
        created_at: float,
        resume_count: int = 0,
    ) -> bool:
        
        if self._checkpoint_manager is None:
            return True  # checkpointing disabled entirely — nothing to fail
        try:
            self._checkpoint_manager.checkpoint(
                context, retry_counts, current_step, status, created_at, resume_count
            )
            return True
        except Exception as exc:
            # observable (logged loudly), and the caller is told via the
            # bool return — never silently treated as a successful write
            logger.error(
                "checkpoint failed execution=%s session=%s step=%s: %s",
                context.trace_id, context.state.session_id, current_step, exc,
            )
            return False

    @staticmethod
    def _enforce_failure_invariants(
        context: RuntimeContext,
        step: RuntimeStep,
        tool_result: ToolResult | None,
        decision: ReflectionDecision,
    ) -> ReflectionDecision:
        
        tool_failed = not (tool_result and tool_result.success)

        if tool_failed and decision.action in (ReflectionAction.COMPLETE, ReflectionAction.CONTINUE):
            logger.error(
                "execution=%s session=%s step=%s: Reflection returned %s for a failed "
                "step — not permitted, overriding to ABORT. Original reason: %s",
                context.trace_id, context.state.session_id,
                step.name, decision.action.value, decision.reason,
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
    def _enforce_retry_step_invariant(
        context: RuntimeContext, step: RuntimeStep, decision: ReflectionDecision
    ) -> ReflectionDecision:
       
        if decision.action != ReflectionAction.RETRY or decision.retry_step is None:
            return decision

        if decision.retry_step != step.name:
            logger.error(
                "execution=%s session=%s step=%s: Reflection RETRY named step '%s', "
                "which the runtime is not currently processing — refusing to silently "
                "retry the wrong step. Overriding to ABORT.",
                context.trace_id, context.state.session_id, step.name, decision.retry_step,
            )
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=(
                    f"RETRY named step '{decision.retry_step}', but the runtime was "
                    f"processing step '{step.name}' — retrying a different step mid-plan "
                    f"isn't supported, so aborting rather than silently retrying the "
                    f"wrong one. Original reason: {decision.reason}"
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

    async def _reflect(
        self, context: RuntimeContext, step: RuntimeStep, result: ExecutionResult
    ) -> ReflectionDecision:
        try:
            decision = await self._reflection.reflect(context, result)
        except Exception as exc:
            raise ReflectionError(str(exc)) from exc
        logger.info(
            "reflection execution=%s session=%s step=%s action=%s source=%s reason=%s",
            context.trace_id, context.state.session_id, step.name,
            decision.action.value, decision.source, decision.reason,
        )
        return decision

    def _finalize(
        self,
        context: RuntimeContext,
        result: ExecutionResult,
        decision: ReflectionDecision,
        checkpoint_durable: bool = True,
    ) -> RuntimeResult:
        metadata = {
            "reflection_action": decision.action.value,
            "reflection_reason": decision.reason,
            "reflection_source": decision.source,
            "execution_id": context.trace_id,
            "checkpoint_durable": checkpoint_durable,
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

        # ToolResult has no formal "answer" concept — stand-in until
        # something further downstream owns turning tool_results into a
        # real response. Currently: last successful tool's data["answer"].
        if not result.tool_results:
            return ""
        last = result.tool_results[-1]
        if isinstance(last.data, dict) and "answer" in last.data:
            return str(last.data["answer"])
        return ""