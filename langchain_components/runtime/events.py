from dataclasses import dataclass, field
from typing import Any

STEP_STARTED = "STEP_STARTED"
STEP_COMPLETED = "STEP_COMPLETED"
STEP_FAILED = "STEP_FAILED"


@dataclass(slots=True)
class RuntimeEvent:
    type: str
    step: str
    data: dict[str, Any] = field(default_factory=dict)