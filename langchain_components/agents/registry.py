from __future__ import annotations

from typing import Iterable

from langchain_components.agents.base_agent import BaseAgent
from langchain_components.agents.exceptions import (
    AgentAlreadyRegisteredError,
    AgentNotFoundError,
)


class AgentRegistry:
    _instance: "AgentRegistry | None" = None

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    @classmethod
    def instance(cls) -> "AgentRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, agent: BaseAgent, *, overwrite: bool = False) -> None:
        if not overwrite and agent.name in self._agents:
            raise AgentAlreadyRegisteredError(agent.name)
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise AgentNotFoundError(name) from exc

    def has(self, name: str) -> bool:
        return name in self._agents

    def list_agents(self) -> Iterable[BaseAgent]:
        return list(self._agents.values())

    def list_names(self) -> list[str]:
        return sorted(self._agents.keys())

    def describe_all(self) -> list[dict[str, str]]:
        return [
            {"name": a.name, "description": a.description} for a in self.list_agents()
        ]

    def clear(self) -> None:
        self._agents.clear()


agent_registry = AgentRegistry.instance()


def register_agent(cls: type[BaseAgent]) -> type[BaseAgent]:
    instance = cls()
    agent_registry.register(instance)
    return cls