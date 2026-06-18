from langchain_components.registry.workflow_decorator import (register_workflow,)
from langchain_components.routing.intent_types import (IntentType,)
from langchain_components.knowledge.faq_store import (FAQS,)


@register_workflow(IntentType.FAQ)
def faq_workflow(state: dict) -> dict:
    """
    Handles frequently asked business questions.
    """

    question = state["question"].lower()

    for faq_key, faq_data in FAQS.items():

        keywords = faq_data["keywords"]

        if any(keyword in question for keyword in keywords):
            return {
                "answer": faq_data["answer"],
                "faq_key": faq_key,
            }

    return {
        "answer": (
            "I couldn't find a matching FAQ. "
            "Please contact AdiyogiCabz support."
        ),
        "faq_key": None,
    }