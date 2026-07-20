from __future__ import annotations

from typing import Iterable

from langchain_components.tools.base_tool import BaseTool
from langchain_components.tools.exceptions import (
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
)


class ToolRegistry:
    

    _instance: "ToolRegistry | None" = None

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    @classmethod
    def instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, tool: BaseTool, *, overwrite: bool = False) -> None:
        if not overwrite and tool.name in self._tools:
            raise ToolAlreadyRegisteredError(tool.name)
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(name) from exc

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> Iterable[BaseTool]:
        return list(self._tools.values())

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def describe_all(self) -> list[dict]:
        """Shape suitable for handing to a planner/LLM as tool metadata
        (name + description + JSON schema of accepted input)."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.schema.model_json_schema(),
            }
            for tool in self.list_tools()
        ]

    def clear(self) -> None:
        """Test-only helper. Do not call from production code paths."""
        self._tools.clear()


tool_registry = ToolRegistry.instance()


def register_tool(cls: type[BaseTool]) -> type[BaseTool]:
    instance = cls()
    tool_registry.register(instance)
    return cls