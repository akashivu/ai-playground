from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    content: str
    role: str | None = None
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryResult(BaseModel):
    entries: list[MemoryEntry] = Field(default_factory=list)
    count: int = 0
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_entries(
        cls, entries: list[MemoryEntry], source: str | None = None, **kwargs: Any
    ) -> "MemoryResult":
        return cls(entries=entries, count=len(entries), source=source, **kwargs)

    def is_empty(self) -> bool:
        return self.count == 0