

from __future__ import annotations

import re
from typing import Protocol

from .models import VALID_INTENTS


_INTENT_KEYWORDS: dict[str, list[str]] = {
    "BOOKING": [
        r"\bbook(?:ing)?\b", r"\bschedule\b", r"\bcancel\b(?! fee)", r"\bconfirm\b",
        r"\bride\b", r"\bpickup\b", r"\bdrop\b",
    ],
    "POLICY": [
        r"\bpolicy\b", r"\ballow(?:ed)?\b", r"\bpet\b", r"\bdog\b", r"\bcat\b",
        r"\bluggage\b", r"\bbaggage\b", r"\brefund\b", r"\bcancellation fee\b",
        r"\bcan i bring\b", r"\bcan i take\b", r"\brules?\b",
    ],
    "PRICING": [
        r"\bprice\b", r"\bcost\b", r"\bfare\b", r"\bhow much\b", r"\bcharge\b",
        r"\brate\b", r"\bsurcharge\b",
    ],
    "VEHICLE": [
        r"\bvehicle\b", r"\bcar\b", r"\bsuv\b", r"\bsedan\b", r"\btempo\b",
        r"\bxl\b", r"\bcapacity\b", r"\bseats?\b",
    ],
    "CITY": [
        r"\bcity\b", r"\bcities\b", r"\bavailable in\b", r"\boperate in\b",
        r"\bbangalore\b", r"\bbengaluru\b", r"\bmysore\b", r"\bchennai\b",
        r"\bhyderabad\b",
    ],
    "FAQ": [
        r"\bhow do i\b", r"\bhow does\b", r"\bwhat is\b", r"\bcan i\b",
    ],
}


class IntentClassifier(Protocol):
    def classify(self, query: str) -> tuple[str, float]: ...


class RuleBasedIntentClassifier:
    def classify(self, query: str) -> tuple[str, float]:
       
        text = query.lower()
        scores: dict[str, int] = {intent: 0 for intent in _INTENT_KEYWORDS}

        for intent, patterns in _INTENT_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    scores[intent] += 1

        total_votes = sum(scores.values())
        if total_votes == 0:
            return "GENERAL", 0.3

        best_intent = max(scores, key=scores.get)
        confidence = min(0.95, 0.5 + 0.15 * scores[best_intent])

       
        if scores.get("POLICY", 0) > 0 and scores.get("FAQ", 0) > 0:
            best_intent = "POLICY"
            confidence = min(0.95, 0.5 + 0.15 * scores["POLICY"])

        assert best_intent in VALID_INTENTS
        return best_intent, round(confidence, 2)
