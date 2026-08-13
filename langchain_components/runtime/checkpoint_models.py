from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from langchain_components.runtime.models import RuntimeStep


CHECKPOINT_SCHEMA_VERSION = 1


class RuntimeStepSnapshot(BaseModel):
    

    name: str
    tool_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    description: str = ""
    output: dict[str, Any] | None = None
    completed: bool = False

    @classmethod
    def from_step(cls, step: RuntimeStep) -> "RuntimeStepSnapshot":
        return cls(
            name=step.name,
            tool_name=step.tool_name,
            payload=dict(step.payload),
            description=step.description,
            output=dict(step.output) if step.output is not None else None,
            completed=step.completed,
        )

    def to_runtime_step(self) -> RuntimeStep:
        return RuntimeStep(
            name=self.name,
            tool_name=self.tool_name,
            payload=dict(self.payload),
            description=self.description,
            output=dict(self.output) if self.output is not None else None,
            completed=self.completed,
        )


class ExecutionCheckpoint(BaseModel):
    

    schema_version: int = CHECKPOINT_SCHEMA_VERSION

    checkpoint_id: str
    execution_id: str
    session_id: str
    agent: str

    plan_state: list[RuntimeStepSnapshot] = Field(default_factory=list)

    completed_steps: list[str] = Field(default_factory=list)

    current_step: str | None = None

    retry_counts: dict[str, int] = Field(default_factory=dict)

    working_memory: dict[str, Any] = Field(default_factory=dict)

    runtime_metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: float
    updated_at: float