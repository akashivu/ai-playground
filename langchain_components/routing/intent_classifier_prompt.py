from langchain_core.prompts import PromptTemplate
from langchain_components.routing.intent_types import IntentType

_INTENT_DEFINITIONS = (
    "FAQ: Frequently asked questions about a business, service, pricing, or policies.\n"
    "KNOWLEDGE_SEARCH: Questions requiring retrieval from documents or guides.\n"
    "BOOKING: Requests to book, reserve, schedule, or arrange a service.\n"
    "RECOMMENDATION: Requests for trip suggestions, options, or personalized plans.\n"
    "PRICING: Questions about cost, fare, rates, or pricing for trips and services.\n"
    "GENERAL: Greetings, casual conversation, or simple travel-related chat.\n"
    "OUT_OF_DOMAIN: Any request unrelated to travel, tourism, bookings, or pricing — "
    "including coding, writing, tutoring, or general knowledge questions."
)

intent_classifier_prompt = PromptTemplate(
    input_variables=["question"],
    partial_variables={
        "valid_intents": ", ".join(IntentType.values()),
        "intent_definitions": _INTENT_DEFINITIONS,
    },
    template=(
        "You are an intent classifier for a travel and cab booking platform.\n\n"
        "Intent definitions:\n{intent_definitions}\n\n"
        "Valid intents: {valid_intents}\n\n"
        "Question:\n{question}\n\n"
        "Return JSON only.\n"
        'Example: {{"intent": "PRICING"}}'
    ),
)