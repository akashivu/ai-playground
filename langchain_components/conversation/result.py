from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from langchain_components.agents.result import AgentResult
from langchain_components.memory.result import MemoryResult


class ConversationResult(BaseModel):
    success: bool
    response: str | None = None
    agent_name: str | None = None
    agent_result: AgentResult | None = None
    memory_result: MemoryResult | None = None
    execution_time_ms: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, response: str | None, **kwargs: Any) -> "ConversationResult":
        return cls(success=True, response=response, **kwargs)

    @classmethod
    def fail(cls, error: str, **kwargs: Any) -> "ConversationResult":
        return cls(success=False, error=error, **kwargs)