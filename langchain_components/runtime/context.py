from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from langchain_components.runtime.state import RuntimeState


@dataclass(slots=True)
class RuntimeContext:
    state: RuntimeState
    planner: object
    executor: object
    tool_executor: object
    memory_manager: object
    agent_name: str
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))