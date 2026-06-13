from langchain_components.routing.intent_types import IntentType

DOMAIN_NAME = "AdiyogiCabz"

ENABLED_INTENTS = [
    IntentType.GENERAL,
    IntentType.KNOWLEDGE_SEARCH,
    IntentType.FAQ,
    IntentType.BOOKING,
    IntentType.RECOMMENDATION,
]