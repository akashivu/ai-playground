from __future__ import annotations

import re
from typing import Protocol

from .models import VALID_INTENTS


_INTENT_KEYWORDS: dict[str, list[str]] = {
    "BOOKING": [
        r"\bbook me\b",
        r"\bbook (?:a|an|the)\b",
        r"\bcreate (?:a )?booking\b",
        r"\bmake (?:a )?booking\b",
        r"\breserve (?:a|an|the)\b",
        r"\bschedule (?:a|an|the)\b",
        r"\bschedule\b",
        r"\bconfirm (?:my|the)\b",
        r"\bcancel\b(?! fee)",
    ],
    "POLICY": [
        r"\bpolicy\b",
        r"\ballow(?:ed)?\b",
        r"\bpet\b",
        r"\bdog\b",
        r"\bcat\b",
        r"\bluggage\b",
        r"\bbaggage\b",
        r"\brefund\b",
        r"\bcancellation fee\b",
        r"\bcan i bring\b",
        r"\bcan i take\b",
        r"\brules?\b",
    ],
    "PRICING": [
        r"\bprice\b",
        r"\bcost\b",
        r"\bfare\b",
        r"\bhow much\b",
        r"\bcharge\b",
        r"\brate\b",
        r"\bsurcharge\b",
    ],
    "VEHICLE": [
        r"\bvehicle\b",
        r"\bcar\b",
        r"\bsuv\b",
        r"\bsedan\b",
        r"\btempo\b",
        r"\bxl\b",
        r"\bcapacity\b",
        r"\bseats?\b",
    ],
    "CITY": [
        r"\bcity\b",
        r"\bcities\b",
        r"\bavailable in\b",
        r"\boperate in\b",
        r"\bbangalore\b",
        r"\bbengaluru\b",
        r"\bmysore\b",
        r"\bchennai\b",
        r"\bhyderabad\b",
    ],
    "FAQ": [
        r"\bhow do i\b",
        r"\bhow does\b",
        r"\bwhat is\b",
        r"\bwhat are\b",
        r"\bcan i\b",
        r"\bcan we\b",
        r"\bis it possible\b",
        r"\bis .* available\b",
        r"\bdo you support\b",
        r"\bdoes .* support\b",
        r"\bwhat happens\b",
        r"\bwhen can i\b",
        r"\bwhere can i\b",
    ],
}


_INFORMATIONAL_PATTERNS = [
    r"^\s*can i\b",
    r"^\s*can we\b",
    r"\bis it possible\b",
    r"\bdo you support\b",
    r"\bdoes .* support\b",
    r"\bhow do i\b",
    r"\bhow does\b",
    r"\bwhat is\b",
    r"\bwhat are\b",
    r"\bwhat happens\b",
    r"\bwhen can i\b",
    r"\bwhere can i\b",
    r"\bis .* available\b",
]


_BOOKING_ACTION_PATTERNS = [
    r"\bbook me\b",
    r"\bbook (?:a|an|the)\b",
    r"\bcreate (?:a )?booking\b",
    r"\bmake (?:a )?booking\b",
    r"\breserve (?:a|an|the)\b",
    r"\bschedule (?:a|an|the)\b",
    r"\bconfirm (?:my|the)\b",
]


class IntentClassifier(Protocol):
    def classify(self, query: str) -> tuple[str, float]:
        ...


class RuleBasedIntentClassifier:
    def classify(self, query: str) -> tuple[str, float]:
        text = query.strip().lower()

        if not text:
            return "GENERAL", 0.3

        

        if self._matches_any(
            text,
            _BOOKING_ACTION_PATTERNS,
        ):
            return "BOOKING", 0.95

        

        if self._matches_any(
            text,
            _INFORMATIONAL_PATTERNS,
        ):
            return "FAQ", 0.90

  

        scores: dict[str, int] = {
            intent: 0
            for intent in _INTENT_KEYWORDS
        }

        for intent, patterns in _INTENT_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    scores[intent] += 1

        total_votes = sum(scores.values())

        if total_votes == 0:
            return "GENERAL", 0.3

        

        if (
            scores["POLICY"] > 0
            and scores["FAQ"] > 0
        ):
            confidence = min(
                0.95,
                0.5 + (
                    0.15 * scores["POLICY"]
                ),
            )
            return "POLICY", round(
                confidence,
                2,
            )

        

        if (
            scores["FAQ"] > 0
            and scores["BOOKING"] > 0
        ):
            return "FAQ", 0.90

        best_intent = max(
            scores,
            key=scores.get,
        )

        confidence = min(
            0.95,
            0.5 + (
                0.15 * scores[best_intent]
            ),
        )

        assert best_intent in VALID_INTENTS

        return best_intent, round(
            confidence,
            2,
        )

    @staticmethod
    def _matches_any(
        text: str,
        patterns: list[str],
    ) -> bool:
        return any(
            re.search(pattern, text)
            for pattern in patterns
        )