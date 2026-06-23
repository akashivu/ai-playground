from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.knowledge.pricing_store import PRICING
from langchain_components.chains.topic_match_chain import build_topic_match_chain


_pricing_matcher = build_topic_match_chain(list(PRICING.keys()))


@register_workflow(IntentType.PRICING)
def pricing_workflow(state: dict) -> dict:
    """Handles pricing queries using semantic topic matching."""
    result = _pricing_matcher.invoke({"question": state["question"]})
    matched_key = result.get("matched_key", "NONE")

    if matched_key in PRICING:
        return {"answer": PRICING[matched_key]}

    return {
        "answer": (
            "Pricing varies based on route, vehicle type, and trip requirements. "
            "Please contact AdiyogiCabz for an accurate quote."
        )
    }