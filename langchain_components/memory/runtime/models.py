from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkingMemory:
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SessionMemory:
    session_id: str
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LongTermMemory:
    user_id: str
    variables: dict[str, Any] = field(default_factory=dict)