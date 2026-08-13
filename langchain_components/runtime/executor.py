from __future__ import annotations

import logging

from langchain_components.runtime.context import RuntimeContext
from langchain_components.runtime.events import (
    STEP_COMPLETED,
    STEP_FAILED,
    STEP_STARTED,
    RuntimeEvent,
)
from langchain_components.runtime.exceptions import StepExecutionError
from langchain_components.runtime.models import RuntimeStep
from langchain_components.tools.exceptions import ToolNotFoundError
from langchain_components.tools.schemas import (
    ToolCallContext,
    ToolResult,
)


logger = logging.getLogger(__name__)


class RuntimeExecutor:
    

    async def execute_step(
        self,
        context: RuntimeContext,
        step: RuntimeStep,
    ) -> tuple[ToolResult, list[RuntimeEvent]]:
        events = [
            RuntimeEvent(
                type=STEP_STARTED,
                step=step.name,
            )
        ]

        tool_call_context = ToolCallContext(
            session_id=context.state.session_id,user_id=context.state.user_id,agent_name=context.agent_name,trace_id=context.trace_id,
            metadata={
                "idempotency_key": (
                    f"{context.trace_id}:{step.name}")},)

        try:
            result = await context.tool_executor.run(step.tool_name, step.payload,tool_call_context,)

        except ToolNotFoundError as exc:
            events.append(RuntimeEvent(type=STEP_FAILED,step=step.name,data={"error": str(exc),},))

            logger.error("tool not found step=%s tool=%s",step.name,step.tool_name,)

            raise StepExecutionError(step.name,str(exc),events=events,) from exc

        step.output = (
            result.data
            if isinstance(result.data, dict)else {"data": result.data})

        step.completed = result.success

        event_type = (
            STEP_COMPLETED
            if result.success
            else STEP_FAILED
        )

        events.append(
            RuntimeEvent(
                type=event_type,
                step=step.name,
                data={
                    "duration_ms": result.duration_ms,
                    "retries": result.retries,
                },
            )
        )

        logger.info(
            "%s -> %s (%.1fms, retries=%d)",
            step.name,
            "SUCCESS" if result.success else "FAILED",
            result.duration_ms or 0.0,
            result.retries,
        )

        self._update_memory(
            context,
            result,
        )

        return result, events

    @staticmethod
    def _update_memory(
        context: RuntimeContext,
        tool_result: ToolResult,
    ) -> None:
        context.memory_manager.save_tool_result(
            context.state,
            tool_result,
        )