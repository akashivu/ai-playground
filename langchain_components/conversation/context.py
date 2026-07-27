from __future__ import annotations

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class ConversationContext(BaseModel):
    user_id: str | None = None
    session_id: str | None = None
    conversation_id: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)