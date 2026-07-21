from __future__ import annotations

import abc
from typing import Any, ClassVar

from langchain_components.planners.context import PlannerContext
from langchain_components.planners.result import ExecutionPlan


class BasePlanner(abc.ABC):
    name: ClassVar[str]
    description: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC in cls.__bases__:
            return
        for attr in ("name", "description"):
            if getattr(cls, attr, None) is None:
                raise TypeError(f"{cls.__name__} must define class attribute '{attr}'")

    @abc.abstractmethod
    async def create_plan(
        self, request: dict[str, Any], context: PlannerContext
    ) -> ExecutionPlan:
        raise NotImplementedError