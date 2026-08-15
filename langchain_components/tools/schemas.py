from __future__ import annotations

import enum
import time
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolErrorType(str, enum.Enum):
    """Structured failure category — set by ToolExecutor, not inferred from error message text by anything downstream (e.g. Reflection)."""

    NOT_FOUND = "not_found"
    VALIDATION = "validation"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    EXECUTION = "execution"


class ToolResult(BaseModel):

    success: bool
    data: Any = None
    error: str | None = None
    error_type: ToolErrorType | None = None
    tool_name: str | None = None
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    duration_ms: float | None = None
    retries: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, data: Any = None, **kwargs: Any) -> "ToolResult":
        return cls(success=True, data=data, **kwargs)

    @classmethod
    def fail(
        cls, error: str, error_type: ToolErrorType | None = None, **kwargs: Any
    ) -> "ToolResult":
        return cls(success=False, error=error, error_type=error_type, **kwargs)


class ToolCallContext(BaseModel):
    

    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str | None = None
    user_id: str | None = None
    agent_name: str | None = None
    plan_id: str | None = None
    task_id: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requested_at: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolAuditRecord(BaseModel):
   

    trace_id: str
    tool_name: str
    execution_id: str
    session_id: str | None = None
    user_id: str | None = None
    agent_name: str | None = None
    request_payload: dict[str, Any]
    success: bool
    error: str | None = None
    duration_ms: float
    retries: int
    timestamp: float = Field(default_factory=time.time)