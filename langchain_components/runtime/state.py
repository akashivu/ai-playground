from __future__ import annotations

from dataclasses import dataclass, field

from langchain_components.memory.runtime.models import LongTermMemory, SessionMemory, WorkingMemory
from langchain_components.runtime.models import RuntimeStep


@dataclass(slots=True)
class RuntimeState:
    agent: str
    session_id: str
    user_id: str
    query: str
    plan: list[RuntimeStep] = field(default_factory=list)
    working_memory: WorkingMemory = field(default_factory=WorkingMemory)
    session_memory: SessionMemory | None = None
    long_term_memory: LongTermMemory | None = None