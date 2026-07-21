from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StepResult(BaseModel):
    step_id: str
    tool_name: str
    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: float | None = None


class ExecutionResult(BaseModel):
    success: bool
    step_results: list[StepResult] = Field(default_factory=list)
    failed_step: str | None = None
    execution_time_ms: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, step_results: list[StepResult], **kwargs: Any) -> "ExecutionResult":
        return cls(success=True, step_results=step_results, **kwargs)

    @classmethod
    def fail(cls, error: str, **kwargs: Any) -> "ExecutionResult":
        return cls(success=False, error=error, **kwargs)