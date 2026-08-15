

from __future__ import annotations

from dataclasses import dataclass, field


VALID_INTENTS = {"FAQ", "BOOKING", "POLICY", "CITY", "VEHICLE", "PRICING", "GENERAL"}


@dataclass(slots=True)
class Entity:
    text: str          # the raw span matched in the query, e.g. "dog"
    label: str         # canonical entity type, e.g. "PET"
    normalized: str     # canonical value, e.g. "pet"


@dataclass(slots=True)
class QueryUnderstanding:
    original_query: str
    rewritten_query: str = ""
    intent: str = "GENERAL"
    category: str | None = None
    categories: list[tuple[str, float]] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    confidence: float = 0.0
    language: str = "en"
    ambiguous: bool = False
    clarification_options: list[str] = field(default_factory=list)
    resolved_from_context: bool = False

    def entity_labels(self) -> list[str]:
        return [e.label for e in self.entities]

    def to_log_dict(self) -> dict:
       
        return {
            "query": self.original_query,
            "language": self.language,
            "intent": self.intent,
            "confidence": self.confidence,
            "entities": self.entity_labels(),
            "categories": self.categories,
            "category": self.category,
            "rewrite": self.rewritten_query,
            "ambiguous": self.ambiguous,
            "resolved_from_context": self.resolved_from_context,
        }

    def __post_init__(self):
        if not self.rewritten_query:
            self.rewritten_query = self.original_query
