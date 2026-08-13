from __future__ import annotations

import asyncio
import logging
from typing import Protocol

from langchain_components.runtime.checkpoint import CheckpointManager
from langchain_components.runtime.context import RuntimeContext
from langchain_components.runtime.events import RuntimeEvent
from langchain_components.runtime.exceptions import (
    CheckpointError,
    CheckpointPersistenceError,
    ExecutionError,
    PlanningError,
    ReflectionError,
    StepExecutionError,
)
from langchain_components.runtime.executor import RuntimeExecutor
from langchain_components.memory.runtime.manager import MemoryManager
from langchain_components.memory.runtime.models import WorkingMemory
from langchain_components.runtime.models import (
    ExecutionResult,
    RuntimeResult,
    RuntimeStep,
)
from langchain_components.runtime.reflection import ReflectionEngine
from langchain_components.runtime.reflection_models import (
    ReflectionAction,
    ReflectionDecision,
)
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
        checkpoint_manager: CheckpointManager | None = None,
    ) -> None:
        self._executor = executor or RuntimeExecutor()
        self._memory = memory or MemoryManager()
        self._reflection = reflection or ReflectionEngine()
        self._max_retries = max_retries
        self._checkpoint_manager = checkpoint_manager

    

    def execute(
        self,
        agent: BaseAgent,
        state: RuntimeState,
    ) -> RuntimeResult:
        return asyncio.run(
            self.execute_async(
                agent,
                state,
            )
        )

    async def execute_async(
        self,
        agent: BaseAgent,
        state: RuntimeState,
    ) -> RuntimeResult:
        context = RuntimeContext(
            state=state,
            planner=agent.planner,
            executor=self._executor,
            tool_executor=agent.tool_executor,
            memory_manager=self._memory,
            agent_name=agent.name,
        )

        logger.info(
            "runtime started agent=%s session=%s execution=%s",
            agent.name,
            state.session_id,
            context.trace_id,
        )

        self._load_memory(context)

        self._plan(context)

        result, decision = await self._run_control_loop(
            context
        )

        self._save_memory(context)

        return self._finalize(
            context,
            result,
            decision,
        )


    def resume(
        self,
        agent: BaseAgent,
        session_id: str,
        execution_id: str,
        user_input: str | None = None,
    ) -> RuntimeResult:
        return asyncio.run(
            self.resume_async(
                agent=agent,
                session_id=session_id,
                execution_id=execution_id,
                user_input=user_input,
            )
        )

    async def resume_async(
        self,
        agent: BaseAgent,
        session_id: str,
        execution_id: str,
        user_input: str | None = None,
    ) -> RuntimeResult:
        

        if self._checkpoint_manager is None:
            raise CheckpointError(
                "Checkpointing is not configured."
            )

        checkpoint = self._checkpoint_manager.restore(
            execution_id=execution_id,
            session_id=session_id,
        )

        state = RuntimeState(
            agent=checkpoint.agent,
            session_id=checkpoint.session_id,
            user_id=checkpoint.runtime_metadata.get(
                "user_id",
                "",
            ),
            query=checkpoint.runtime_metadata.get(
                "query",
                "",
            ),
            plan=[
                snapshot.to_runtime_step()
                for snapshot in checkpoint.plan_state
            ],
        )

        context = RuntimeContext(
            state=state,
            planner=agent.planner,
            executor=self._executor,
            tool_executor=agent.tool_executor,
            memory_manager=self._memory,
            agent_name=agent.name,
            trace_id=execution_id,
        )

        logger.info(
            "runtime resuming agent=%s session=%s execution=%s",
            agent.name,
            session_id,
            execution_id,
        )

        self._load_memory(context)

        context.state.working_memory = WorkingMemory(
            variables=dict(
                checkpoint.working_memory
            )
        )

    

        if user_input is not None:
            normalized_input = user_input.strip()

            if normalized_input:
                context.state.query = normalized_input

                context.state.working_memory.variables[
                    "last_user_input"
                ] = normalized_input

                context.state.working_memory.variables[
                    "resume_input"
                ] = normalized_input

                logger.info(
                    "resume input received execution=%s",
                    execution_id,
                )

        retry_counts = dict(
            checkpoint.retry_counts
        )

        result, decision = await self._run_control_loop(
            context,
            retry_counts=retry_counts,
        )

        self._save_memory(context)

        return self._finalize(
            context,
            result,
            decision,
        )

  

    def _load_memory(
        self,
        context: RuntimeContext,
    ) -> None:
        logger.info(
            "memory load started"
        )

        self._memory.load(
            context.state
        )

        logger.info(
            "memory load finished"
        )

    def _save_memory(
        self,
        context: RuntimeContext,
    ) -> None:
        logger.info(
            "memory save started"
        )

        self._memory.save(
            context.state
        )

        logger.info(
            "memory save finished"
        )

  

    def _plan(
        self,
        context: RuntimeContext,
    ) -> list[RuntimeStep]:
        logger.info(
            "planning started"
        )

        try:
            plan = context.planner.create_plan(
                context.state
            )

        except Exception as exc:
            raise PlanningError(
                str(exc)
            ) from exc

        context.state.plan = plan

        logger.info(
            "planning finished steps=%d",
            len(plan),
        )

        return plan

    

    async def _run_control_loop(
        self,
        context: RuntimeContext,
        retry_counts: dict[str, int] | None = None,
    ) -> tuple[
        ExecutionResult,
        ReflectionDecision,
    ]:
        completed_steps: list[str] = []
        tool_results: list[ToolResult] = []
        events: list[RuntimeEvent] = []

        retry_counts = (
            retry_counts
            if retry_counts is not None
            else {}
        )

        if not context.state.plan:
            decision = ReflectionDecision(
                action=ReflectionAction.COMPLETE,
                reason="Empty plan.",
            )

            return (
                self._accumulated_result(
                    completed_steps,
                    tool_results,
                    events,
                    None,
                ),
                decision,
            )

        for step in context.state.plan:

           

            if step.completed:
                completed_steps.append(
                    step.name
                )
                continue


            while True:
                tool_result, step_events = (
                    await self._execute_one_step(
                        context,
                        step,
                    )
                )

                events.extend(
                    step_events
                )

                if tool_result is not None:
                    tool_results.append(
                        tool_result
                    )

                step_result = self._step_result(
                    step,
                    tool_result,
                )

                decision = await self._reflect(
                    context,
                    step_result,
                )

                decision = (
                    self._enforce_failure_invariants(
                        step,
                        tool_result,
                        decision,
                    )
                )


                if decision.action == ReflectionAction.RETRY:
                    attempt = retry_counts.get(
                        step.name,
                        0,
                    )

                    if attempt < self._max_retries:
                        retry_counts[
                            step.name
                        ] = attempt + 1

                        logger.info(
                            "retrying step=%s attempt=%d/%d",
                            step.name,
                            attempt + 1,
                            self._max_retries,
                        )

                        self._checkpoint_or_fail(
                            context=context,
                            retry_counts=retry_counts,
                            current_step=step.name,
                            pending_user_input=None,
                        )

                        continue

                    decision = ReflectionDecision(
                        action=ReflectionAction.ABORT,
                        reason=(
                            f"Step '{step.name}' "
                            f"failed after "
                            f"{self._max_retries} retries."
                        ),
                        source="runtime",
                    )

                    self._checkpoint_or_fail(
                        context=context,
                        retry_counts=retry_counts,
                        current_step=step.name,
                        pending_user_input=None,
                    )

                    result = self._accumulated_result(
                        completed_steps,
                        tool_results,
                        events,
                        step.name,
                    )

                    return result, decision

                

                if decision.action == ReflectionAction.CONTINUE:
                    completed_steps.append(
                        step.name
                    )

                    self._checkpoint_or_fail(
                        context=context,
                        retry_counts=retry_counts,
                        current_step=None,
                        pending_user_input=None,
                    )

                    break

               

                if decision.action == ReflectionAction.COMPLETE:
                    completed_steps.append(
                        step.name
                    )

                    self._checkpoint_or_fail(
                        context=context,
                        retry_counts=retry_counts,
                        current_step=None,
                        pending_user_input=None,
                    )

                    result = self._accumulated_result(
                        completed_steps,
                        tool_results,
                        events,
                        None,
                    )

                    return result, decision

                

                failed_step = (
                    step.name
                    if not (
                        tool_result
                        and tool_result.success
                    )
                    else None
                )

                pending_user_input = (
                    decision.ask_user_message
                    if decision.action
                    == ReflectionAction.ASK_USER
                    else None
                )

                self._checkpoint_or_fail(
                    context=context,
                    retry_counts=retry_counts,
                    current_step=step.name,
                    pending_user_input=pending_user_input,
                )

                result = self._accumulated_result(
                    completed_steps,
                    tool_results,
                    events,
                    failed_step,
                )

                return result, decision

        

        decision = ReflectionDecision(
            action=ReflectionAction.COMPLETE,
            reason="All steps already completed.",
        )

        return (
            self._accumulated_result(
                completed_steps,
                tool_results,
                events,
                None,
            ),
            decision,
        )



    async def _execute_one_step(
        self,
        context: RuntimeContext,
        step: RuntimeStep,
    ) -> tuple[
        ToolResult | None,
        list[RuntimeEvent],
    ]:
        try:
            return await context.executor.execute_step(
                context,
                step,
            )

        except StepExecutionError as exc:
            return None, exc.events

        except Exception as exc:
            raise ExecutionError(
                str(exc)
            ) from exc

  

    def _checkpoint_or_fail(
        self,
        context: RuntimeContext,
        retry_counts: dict[str, int],
        current_step: str | None,
        pending_user_input: str | None,
    ) -> None:
        

        if self._checkpoint_manager is None:
            return

        try:
            self._checkpoint_manager.checkpoint(
                context=context,
                retry_counts=retry_counts,
                current_step=current_step,
                pending_user_input=pending_user_input,
            )

        except Exception as exc:
            logger.exception(
                "checkpoint persistence failed "
                "execution=%s step=%s",
                context.trace_id,
                current_step,
            )

            raise CheckpointPersistenceError(
                execution_id=context.trace_id,
                step=current_step,
                detail=str(exc),
            ) from exc

  

    @staticmethod
    def _enforce_failure_invariants(
        step: RuntimeStep,
        tool_result: ToolResult | None,
        decision: ReflectionDecision,
    ) -> ReflectionDecision:
        tool_failed = not (
            tool_result
            and tool_result.success
        )

        if (
            tool_failed
            and decision.action
            in (
                ReflectionAction.COMPLETE,
                ReflectionAction.CONTINUE,
            )
        ):
            logger.error(
                "Reflection returned %s for failed "
                "step=%s; overriding to ABORT",
                decision.action.value,
                step.name,
            )

            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=(
                    "Failed tool execution cannot "
                    f"produce {decision.action.value}."
                ),
                source="runtime",
            )

        return decision

   

    @staticmethod
    def _step_result(
        step: RuntimeStep,
        tool_result: ToolResult | None,
    ) -> ExecutionResult:
        success = bool(
            tool_result
            and tool_result.success
        )

        return ExecutionResult(
            success=success,
            completed_steps=(
                [step.name]
                if success
                else []
            ),
            tool_results=(
                [tool_result]
                if tool_result
                else []
            ),
            failed_step=(
                None
                if success
                else step.name
            ),
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
        self,
        context: RuntimeContext,
        result: ExecutionResult,
    ) -> ReflectionDecision:
        try:
            decision = await self._reflection.reflect(
                context,
                result,
            )

        except Exception as exc:
            raise ReflectionError(
                str(exc)
            ) from exc

        logger.info(
            "reflection action=%s source=%s reason=%s",
            decision.action.value,
            decision.source,
            decision.reason,
        )

        return decision



    def _finalize(
        self,
        context: RuntimeContext,
        result: ExecutionResult,
        decision: ReflectionDecision,
    ) -> RuntimeResult:
        metadata = {
            "reflection_action": decision.action.value,
            "reflection_reason": decision.reason,
            "reflection_source": decision.source,
            "execution_id": context.trace_id,
        }

        if result.failed_step:
            metadata["failed_step"] = (
                result.failed_step
            )

        if decision.ask_user_message:
            metadata["ask_user_message"] = (
                decision.ask_user_message
            )

        success = (
            result.success
            and decision.action
            != ReflectionAction.ABORT
        )

        return RuntimeResult(success=success,answer=self._extract_answer(result,decision,),
            state=context.state.working_memory.variables,tool_calls=result.completed_steps,metadata=metadata,)

    @staticmethod
    def _extract_answer(
        result: ExecutionResult,
        decision: ReflectionDecision,
    ) -> str:
        if (
            decision.action
            == ReflectionAction.ASK_USER
            and decision.ask_user_message
        ):
            return decision.ask_user_message

        if not result.tool_results:
            return ""

        last = result.tool_results[-1]

        if (
            isinstance(last.data, dict)
            and "answer" in last.data
        ):
            return str(
                last.data["answer"]
            )

        return ""