from __future__ import annotations

import time

from langchain_components.execution.context import ExecutionContext
from langchain_components.execution.exceptions import (
    PlanValidationError,
    StepDependencyError,
)
from langchain_components.execution.result import ExecutionResult, StepResult
from langchain_components.planners.result import ExecutionPlan, PlanStep
from langchain_components.tools.exceptions import ToolNotFoundError
from langchain_components.tools.executor import ToolExecutor
from langchain_components.tools.executor import tool_executor as default_tool_executor
from langchain_components.tools.schemas import ToolCallContext


class PlanExecutor:
    def __init__(self, tool_executor: ToolExecutor | None = None) -> None:
        self.tool_executor = tool_executor or default_tool_executor

    async def execute_plan(
        self, plan: ExecutionPlan, context: ExecutionContext
    ) -> ExecutionResult:
        start = time.perf_counter()
        tool_executor = context.tool_executor or self.tool_executor

        try:
            self._validate_plan(plan, tool_executor)
        except PlanValidationError as exc:
            return ExecutionResult.fail(
                error=str(exc), execution_time_ms=self._elapsed(start)
            )

        step_results: list[StepResult] = []
        completed_step_ids: set[str] = set()

        for step in plan.steps:
            if not self._dependencies_satisfied(step, completed_step_ids):
                dep_error = StepDependencyError(step.step_id, step.depends_on)
                step_results.append(
                    StepResult(
                        step_id=step.step_id,
                        tool_name=step.tool_name,
                        success=False,
                        error=str(dep_error),
                    )
                )
                return ExecutionResult.fail(
                    error=str(dep_error),
                    step_results=step_results,
                    failed_step=step.step_id,
                    execution_time_ms=self._elapsed(start),
                )

            step_result = await self._run_step(step, context, tool_executor)
            step_results.append(step_result)

            if not step_result.success:
                return ExecutionResult.fail(
                    error=f"Step '{step.step_id}' ({step.tool_name}) failed: {step_result.error}",
                    step_results=step_results,
                    failed_step=step.step_id,
                    execution_time_ms=self._elapsed(start),
                )

            completed_step_ids.add(step.step_id)

        return ExecutionResult.ok(
            step_results=step_results,
            execution_time_ms=self._elapsed(start),
            metadata=plan.metadata,
        )

    async def _run_step(
        self, step: PlanStep, context: ExecutionContext, tool_executor: ToolExecutor
    ) -> StepResult:
        step_start = time.perf_counter()
        tool_call_context = ToolCallContext(
            session_id=context.session_id,
            user_id=context.user_id,
            trace_id=context.trace_id,
            metadata=context.metadata,
        )
        try:
            tool_result = await tool_executor.run(
                step.tool_name, step.input, tool_call_context
            )
        except ToolNotFoundError as exc:
            return StepResult(
                step_id=step.step_id,
                tool_name=step.tool_name,
                success=False,
                error=str(exc),
                duration_ms=(time.perf_counter() - step_start) * 1000,
            )
        except Exception as exc:  # noqa: BLE001
            return StepResult(
                step_id=step.step_id,
                tool_name=step.tool_name,
                success=False,
                error=str(exc),
                duration_ms=(time.perf_counter() - step_start) * 1000,
            )

        return StepResult(
            step_id=step.step_id,
            tool_name=step.tool_name,
            success=tool_result.success,
            output=tool_result.data,
            error=tool_result.error,
            duration_ms=(time.perf_counter() - step_start) * 1000,
        )

    def _validate_plan(self, plan: ExecutionPlan, tool_executor: ToolExecutor) -> None:
        seen_ids: set[str] = set()
        for index, step in enumerate(plan.steps):
            if not step.tool_name:
                raise PlanValidationError(
                    f"step at index {index} is missing a tool_name"
                )
            if step.step_id in seen_ids:
                raise PlanValidationError(f"duplicate step_id '{step.step_id}'")
            for dep in step.depends_on:
                if dep not in seen_ids:
                    raise PlanValidationError(
                        f"step '{step.step_id}' depends on '{dep}', which does not "
                        "appear before it in the plan"
                    )
            if not tool_executor.registry.has(step.tool_name):
                raise PlanValidationError(
                    f"step '{step.step_id}' references unknown tool '{step.tool_name}'"
                )
            seen_ids.add(step.step_id)

    @staticmethod
    def _dependencies_satisfied(step: PlanStep, completed_step_ids: set[str]) -> bool:
        return all(dep in completed_step_ids for dep in step.depends_on)

    @staticmethod
    def _elapsed(start: float) -> float:
        return (time.perf_counter() - start) * 1000


plan_executor = PlanExecutor()