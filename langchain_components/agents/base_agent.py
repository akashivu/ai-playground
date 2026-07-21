from __future__ import annotations

import abc
import time
from typing import Any, ClassVar

from langchain_components.agents.context import AgentContext
from langchain_components.agents.exceptions import ExecutionError, PlanningError
from langchain_components.agents.result import AgentResult
from langchain_components.execution.context import ExecutionContext
from langchain_components.execution.executor import PlanExecutor
from langchain_components.execution.executor import (
    plan_executor as default_plan_executor,
)
from langchain_components.execution.result import ExecutionResult
from langchain_components.planners.base_planner import BasePlanner
from langchain_components.planners.context import PlannerContext
from langchain_components.planners.result import ExecutionPlan
from langchain_components.tools.executor import ToolExecutor
from langchain_components.tools.executor import tool_executor as default_tool_executor


class BaseAgent(abc.ABC):
    name: ClassVar[str]
    description: ClassVar[str]

    def __init__(
        self,
        tool_executor: ToolExecutor | None = None,
        planner: BasePlanner | None = None,
        plan_executor: PlanExecutor | None = None,
    ) -> None:
        self.tool_executor = tool_executor or default_tool_executor
        self.planner = planner
        self.plan_executor = plan_executor or default_plan_executor

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC in cls.__bases__:
            return
        for attr in ("name", "description"):
            if getattr(cls, attr, None) is None:
                raise TypeError(f"{cls.__name__} must define class attribute '{attr}'")

    async def run(self, request: dict[str, Any], context: AgentContext) -> AgentResult:
        start = time.perf_counter()

        try:
            context = await self.prepare_context(request, context)
        except Exception as exc:
            error = (
                exc
                if isinstance(exc, PlanningError)
                else PlanningError(self.name, str(exc))
            )
            return self._failure(error, start)

        try:
            plan = await self.plan(request, context)
        except Exception as exc:
            error = (
                exc
                if isinstance(exc, PlanningError)
                else PlanningError(self.name, str(exc))
            )
            return self._failure(error, start)

        try:
            result = await self.execute(plan, context)
        except Exception as exc:
            error = (
                exc
                if isinstance(exc, ExecutionError)
                else ExecutionError(self.name, str(exc))
            )
            return self._failure(error, start)

        result.agent_name = self.name
        result.plan = plan
        result.execution_time_ms = (time.perf_counter() - start) * 1000
        return result

    async def prepare_context(
        self, request: dict[str, Any], context: AgentContext
    ) -> AgentContext:
        return context

    async def plan(
        self, request: dict[str, Any], context: AgentContext
    ) -> ExecutionPlan:
        if self.planner is None:
            raise PlanningError(self.name, "no planner configured for this agent")
        planner_context = self._build_planner_context(request, context)
        return await self.planner.create_plan(request, planner_context)

    def _build_planner_context(
        self, request: dict[str, Any], context: AgentContext
    ) -> PlannerContext:
        return PlannerContext(
            intent=context.intent,
            conversation_history=context.conversation_history,
            workflow=context.workflow,
            metadata=context.metadata,
            available_tools=self.tool_executor.registry.describe_all(),
        )

    async def execute(self, plan: Any, context: AgentContext) -> AgentResult:
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionError(
                self.name,
                "default execute() requires an ExecutionPlan - override execute() "
                "for agents that plan() with a custom structure",
            )
        execution_context = self._build_execution_context(context)
        execution_result = await self.plan_executor.execute_plan(
            plan, execution_context
        )
        return self._to_agent_result(execution_result)

    def _build_execution_context(self, context: AgentContext) -> ExecutionContext:
        return ExecutionContext(
            user_id=context.user_id,
            session_id=context.session_id,
            tool_executor=self.tool_executor,
            trace_id=context.trace_id,
            metadata=context.metadata,
        )

    def _to_agent_result(self, execution_result: ExecutionResult) -> AgentResult:
        tool_calls = [step.model_dump() for step in execution_result.step_results]
        if execution_result.success:
            return AgentResult.ok(
                response=f"Completed {len(execution_result.step_results)} step(s).",
                tool_calls=tool_calls,
                metadata=execution_result.metadata,
            )
        return AgentResult.fail(
            error=execution_result.error or "execution failed",
            tool_calls=tool_calls,
            metadata={
                "failed_step": execution_result.failed_step,
                **execution_result.metadata,
            },
        )

    def _failure(self, error: Exception, start: float) -> AgentResult:
        return AgentResult.fail(
            error=str(error),
            agent_name=self.name,
            execution_time_ms=(time.perf_counter() - start) * 1000,
        )