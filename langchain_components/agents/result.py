from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    success: bool
    response: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: float | None = None
    plan: Any = None
    error: str | None = None
    agent_name: str | None = None

    @classmethod
    def ok(cls, response: str, **kwargs: Any) -> "AgentResult":
        return cls(success=True, response=response, **kwargs)

    @classmethod
    def fail(cls, error: str, **kwargs: Any) -> "AgentResult":
        return cls(success=False, error=error, **kwargs)