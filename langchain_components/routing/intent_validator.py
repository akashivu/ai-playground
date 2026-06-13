from langchain_components.routing.intent_types import IntentType
from domains.domain_manager import get_active_domain


def validate_intent(intent: IntentType) -> IntentType:
    """Validates whether an intent is enabled for the active domain."""
    enabled_intents = get_active_domain()["enabled_intents"]
    if intent not in enabled_intents:
        raise ValueError(f"Intent '{intent}' is not enabled for this domain.")
    return intent