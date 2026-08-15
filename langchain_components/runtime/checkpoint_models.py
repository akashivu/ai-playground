from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field

from langchain_components.runtime.models import RuntimeStep


CHECKPOINT_SCHEMA_VERSION = 2


class ExecutionStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


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
            payload=step.payload,
            description=step.description,
            output=step.output,
            completed=step.completed,
        )

    def to_runtime_step(self) -> RuntimeStep:
        return RuntimeStep(
            name=self.name,
            tool_name=self.tool_name,
            payload=self.payload,
            description=self.description,
            output=self.output,
            completed=self.completed,
        )


class ExecutionCheckpoint(BaseModel):
   

    schema_version: int = CHECKPOINT_SCHEMA_VERSION
    checkpoint_id: str
    execution_id: str
    session_id: str
    agent: str
    status: ExecutionStatus
    plan_state: list[RuntimeStepSnapshot]
    completed_steps: list[str]
    current_step: str | None
    retry_counts: dict[str, int] = Field(default_factory=dict)
    working_memory: dict[str, Any] = Field(default_factory=dict)
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)
    resume_count: int = 0
    created_at: float
    updated_at: float