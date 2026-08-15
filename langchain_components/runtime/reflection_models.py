from __future__ import annotations

import enum
from typing import Literal

from pydantic import BaseModel, Field


class ReflectionAction(str, enum.Enum):
    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    ASK_USER = "ASK_USER"
    COMPLETE = "COMPLETE"
    ABORT = "ABORT"


class ReflectionDecision(BaseModel):
    

    action: ReflectionAction
    reason: str

    
    retry_step: str | None = None

    # required when action == ASK_USER — shown to the user as-is
    ask_user_message: str | None = None

    
    referenced_tool: str | None = None

    source: Literal["deterministic", "llm", "fallback", "runtime"] = "deterministic"


class ReflectionPromptContext(BaseModel):
    

    query: str
    failed_step: str | None
    error: str | None
    remaining_step_names: list[str] = Field(default_factory=list)
    available_tool_names: list[str] = Field(default_factory=list)
    execution_id: str = ""