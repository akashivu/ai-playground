from __future__ import annotations

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    user_id: str | None = None
    session_id: str | None = None
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    workflow: str | None = None
    intent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = Field(default_factory=time.time)