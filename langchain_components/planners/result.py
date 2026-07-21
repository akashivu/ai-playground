from __future__ import annotations

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    tool_name: str
    input: dict[str, Any] = Field(default_factory=dict)
    description: str | None = None
    depends_on: list[str] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str | None = None
    steps: list[PlanStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def step_names(self) -> list[str]:
        return [step.tool_name for step in self.steps]

    def get_step(self, step_id: str) -> PlanStep | None:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None