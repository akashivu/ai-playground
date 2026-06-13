from enum import Enum


class IntentType(str, Enum):
    FAQ = "FAQ"
    KNOWLEDGE_SEARCH = "KNOWLEDGE_SEARCH"
    BOOKING = "BOOKING"
    RECOMMENDATION = "RECOMMENDATION"
    GENERAL = "GENERAL"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]