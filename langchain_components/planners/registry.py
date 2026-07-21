from __future__ import annotations

from typing import Iterable

from langchain_components.planners.base_planner import BasePlanner
from langchain_components.planners.exceptions import (
    PlannerAlreadyRegisteredError,
    PlannerNotFoundError,
)


class PlannerRegistry:
    _instance: "PlannerRegistry | None" = None

    def __init__(self) -> None:
        self._planners: dict[str, BasePlanner] = {}

    @classmethod
    def instance(cls) -> "PlannerRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, planner: BasePlanner, *, overwrite: bool = False) -> None:
        if not overwrite and planner.name in self._planners:
            raise PlannerAlreadyRegisteredError(planner.name)
        self._planners[planner.name] = planner

    def get(self, name: str) -> BasePlanner:
        try:
            return self._planners[name]
        except KeyError as exc:
            raise PlannerNotFoundError(name) from exc

    def has(self, name: str) -> bool:
        return name in self._planners

    def list_planners(self) -> Iterable[BasePlanner]:
        return list(self._planners.values())

    def list_names(self) -> list[str]:
        return sorted(self._planners.keys())

    def describe_all(self) -> list[dict[str, str]]:
        return [
            {"name": p.name, "description": p.description} for p in self.list_planners()
        ]

    def clear(self) -> None:
        self._planners.clear()


planner_registry = PlannerRegistry.instance()


def register_planner(cls: type[BasePlanner]) -> type[BasePlanner]:
    instance = cls()
    planner_registry.register(instance)
    return cls