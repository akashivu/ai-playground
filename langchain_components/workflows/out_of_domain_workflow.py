from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from domains.domain_manager import get_policy


@register_workflow(IntentType.OUT_OF_DOMAIN)
def out_of_domain_workflow(state: dict) -> dict:
    """Returns the domain's refusal message for out-of-domain requests."""
    return {"answer": get_policy().refusal_message}