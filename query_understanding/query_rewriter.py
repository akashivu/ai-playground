

from __future__ import annotations

import re
from typing import Protocol

from .models import Entity


_REWRITE_TEMPLATES: list[tuple[str, str]] = [
    ("REFUND", "refund cancellation policy"),
    ("CANCELLATION", "cancellation policy"),
    ("PET", "pet travel policy"),
    ("LUGGAGE", "luggage policy"),
    ("AIRPORT", "airport pickup transfer"),
    ("VEHICLE_TYPE", "{value} vehicle specification"),
    ("CITY", "{value} service availability"),
    ("BOOKING", "ride booking process"),
]

_NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "couple", "pair"}
_STRONG_ANAPHORA_RE = re.compile(
    r"\b(that one|same|again|another|more|too|as well)\b", re.IGNORECASE
)

_WEAK_ANAPHORA_RE = re.compile(r"\b(it|that|those)\b", re.IGNORECASE)
_WEAK_ANAPHORA_MAX_WORDS = 4


def looks_like_followup(query: str) -> bool:
    text = query.lower()
    words = re.findall(r"[a-zA-Z0-9']+", text)

    if any(w in _NUMBER_WORDS or w.isdigit() for w in words):
        return True
    if _STRONG_ANAPHORA_RE.search(text):
        return True
    if len(words) <= _WEAK_ANAPHORA_MAX_WORDS and _WEAK_ANAPHORA_RE.search(text):
        return True
    return False


class QueryRewriter(Protocol):
    def rewrite(
        self,
        query: str,
        entities: list[Entity],
        previous_entities: list[Entity] | None = None,
    ) -> str: ...


class RuleBasedQueryRewriter:
    def rewrite(
        self,
        query: str,
        entities: list[Entity],
        previous_entities: list[Entity] | None = None,
    ) -> str:
        effective_entities = entities

        if not entities and previous_entities and looks_like_followup(query):
            effective_entities = previous_entities

        entity_by_label = {e.label: e for e in effective_entities}

        for label, template in _REWRITE_TEMPLATES:
            if label in entity_by_label:
                if "{value}" in template:
                    return template.format(value=entity_by_label[label].normalized)
                return template

        return query
