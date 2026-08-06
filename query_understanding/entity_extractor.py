

from __future__ import annotations

import re
from typing import Protocol

from .models import Entity


_ENTITY_PATTERNS: dict[str, tuple[str, str]] = {
    r"\bdog\b": ("PET", "pet"),
    r"\bcat\b": ("PET", "pet"),
    r"\bpets?\b": ("PET", "pet"),
    r"\bgolden retriever\b": ("PET", "pet"),
    r"\blabrador\b": ("PET", "pet"),
    r"\bgerman shepherd\b": ("PET", "pet"),
    r"\bpuppy\b": ("PET", "pet"),
    r"\bkitten\b": ("PET", "pet"),
    r"\bluggage\b": ("LUGGAGE", "luggage"),
    r"\bbaggage\b": ("LUGGAGE", "luggage"),
    r"\bsuitcase\b": ("LUGGAGE", "luggage"),
    r"\brefund\b": ("REFUND", "refund"),
    r"\bcancellation\b": ("CANCELLATION", "cancellation"),
    r"\bairport\b": ("AIRPORT", "airport"),
    r"\bbangalore\b": ("CITY", "bangalore"),
    r"\bbengaluru\b": ("CITY", "bangalore"),
    r"\bmysore\b": ("CITY", "mysore"),
    r"\bchennai\b": ("CITY", "chennai"),
    r"\bhyderabad\b": ("CITY", "hyderabad"),
    r"\bsuv\b": ("VEHICLE_TYPE", "suv"),
    r"\bsedan\b": ("VEHICLE_TYPE", "sedan"),
    r"\btempo\s*traveller\b": ("VEHICLE_TYPE", "tempo traveller"),
    r"\bxl\b": ("VEHICLE_TYPE", "xl"),
    r"\bbooking\b": ("BOOKING", "booking"),
    r"\bride\b": ("BOOKING", "booking"),
}


class EntityExtractor(Protocol):
    def extract(self, query: str) -> list[Entity]: ...


class RuleBasedEntityExtractor:
    def extract(self, query: str) -> list[Entity]:
        text = query.lower()
        entities: list[Entity] = []
        seen_labels: set[tuple[str, str]] = set()

        for pattern, (label, normalized) in _ENTITY_PATTERNS.items():
            match = re.search(pattern, text)
            if match:
                key = (label, normalized)
                if key in seen_labels:
                    continue
                seen_labels.add(key)
                entities.append(
                    Entity(text=match.group(0), label=label, normalized=normalized)
                )

        return entities
