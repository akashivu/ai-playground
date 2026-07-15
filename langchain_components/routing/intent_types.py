from enum import Enum


class IntentType(str, Enum):
    FAQ = "FAQ"
    KNOWLEDGE_SEARCH = "KNOWLEDGE_SEARCH"
    BOOKING = "BOOKING"
    BOOKING_STATUS = "BOOKING_STATUS"
    RECOMMENDATION = "RECOMMENDATION"
    PRICING = "PRICING"
    POLICY = "POLICY"
    GENERAL = "GENERAL"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    ITINERARY = "ITINERARY"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]