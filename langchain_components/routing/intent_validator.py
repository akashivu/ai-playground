from langchain_components.routing.intent_types import IntentType
from domains.domain_manager import get_active_domain


def validate_intent(intent: IntentType) -> IntentType:
    """Validates intent against domain's enabled intents. OUT_OF_DOMAIN always allowed through."""
    if intent == IntentType.OUT_OF_DOMAIN:
        return intent

    enabled_intents = get_active_domain()["enabled_intents"]
    if intent not in enabled_intents:
        raise ValueError(f"Intent '{intent}' is not enabled for this domain.")
    return intent