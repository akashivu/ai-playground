from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langchain_components.runtime.events import RuntimeEvent
from langchain_components.tools.schemas import ToolResult


@dataclass(slots=True)
class RuntimeResult:
    success: bool
    answer: str
    state: dict[str, Any]
    tool_calls: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RuntimeStep:
    name: str
    tool_name: str
    payload: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    output: dict[str, Any] | None = None
    completed: bool = False


@dataclass(slots=True)
class ExecutionResult:
    success: bool
    completed_steps: list[str]
    tool_results: list[ToolResult] = field(default_factory=list)
    runtime_events: list[RuntimeEvent] = field(default_factory=list)
    failed_step: str | None = None