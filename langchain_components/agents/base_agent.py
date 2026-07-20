from __future__ import annotations

import abc
import time
from typing import Any, ClassVar

from langchain_components.agents.context import AgentContext
from langchain_components.agents.exceptions import ExecutionError, PlanningError
from langchain_components.agents.result import AgentResult
from langchain_components.tools.executor import ToolExecutor
from langchain_components.tools.executor import tool_executor as default_tool_executor


class BaseAgent(abc.ABC):
    name: ClassVar[str]
    description: ClassVar[str]

    def __init__(
        self,
        tool_executor: ToolExecutor | None = None,
        planner: Any = None,
    ) -> None:
        self.tool_executor = tool_executor or default_tool_executor
        self.planner = planner

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

    @abc.abstractmethod
    async def plan(self, request: dict[str, Any], context: AgentContext) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def execute(self, plan: Any, context: AgentContext) -> AgentResult:
        raise NotImplementedError

    def _failure(self, error: Exception, start: float) -> AgentResult:
        return AgentResult.fail(
            error=str(error),
            agent_name=self.name,
            execution_time_ms=(time.perf_counter() - start) * 1000,
        )