

from __future__ import annotations

from .models import Entity

_AMBIGUOUS_WORD_COUNT_THRESHOLD = 3
_AMBIGUOUS_CONFIDENCE_THRESHOLD = 0.5


_KNOWN_AMBIGUOUS_CLARIFICATIONS: dict[str, list[str]] = {
    "how much": ["Cab fare", "Cancellation fee", "Rental pricing"],
    "what about": ["Booking", "Pricing", "Vehicle options"],
    "is it available": ["A specific city", "A specific vehicle type"],
}


def detect_ambiguity(
    query: str, entities: list[Entity], intent: str, confidence: float
) -> tuple[bool, list[str]]:
    normalized = query.strip().lower().rstrip("?.")

    if normalized in _KNOWN_AMBIGUOUS_CLARIFICATIONS:
        return True, _KNOWN_AMBIGUOUS_CLARIFICATIONS[normalized]

    word_count = len(query.split())
    if (
        word_count <= _AMBIGUOUS_WORD_COUNT_THRESHOLD
        and not entities
        and confidence < _AMBIGUOUS_CONFIDENCE_THRESHOLD
    ):
        return True, ["Booking", "Pricing", "Policies", "Vehicles"]

    return False, []
