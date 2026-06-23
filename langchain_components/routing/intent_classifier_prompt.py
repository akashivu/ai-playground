from langchain_core.prompts import PromptTemplate
from langchain_components.routing.intent_types import IntentType

_INTENT_DEFINITIONS = (
    "FAQ: Frequently asked questions about policies, services, or business rules.\n"
    "KNOWLEDGE_SEARCH: Questions requiring retrieval from documents, guides, or knowledge base.\n"
    "BOOKING: Requests to book, reserve, schedule, or arrange a cab or service.\n"
    "RECOMMENDATION: Requests for trip suggestions, vehicle recommendations, or travel plans.\n"
    "PRICING: Any question about cost, fare, price, rate, or charges for a trip or service.\n"
    "GENERAL: Greetings, casual conversation, or simple travel-related chat.\n"
    "OUT_OF_DOMAIN: Requests unrelated to travel, bookings, or pricing — "
    "including coding, writing, tutoring, or general knowledge."
)

_EXAMPLES = (
    "Examples:\n"
    "User: How much is airport pickup? → PRICING\n"
    "User: What is the fare for Mysore? → PRICING\n"
    "User: Cab cost to Bangalore airport? → PRICING\n"
    "User: Price for one-way trip? → PRICING\n"
    "User: What is the round-trip cost? → PRICING\n"
    "User: Book a cab to Coorg → BOOKING\n"
    "User: What vehicles do you have? → FAQ\n"
    "User: Suggest a 3-day trip → RECOMMENDATION\n"
    "User: Write Python code → OUT_OF_DOMAIN\n"
    "User: Hello → GENERAL\n"
)

intent_classifier_prompt = PromptTemplate(
    input_variables=["question"],
    partial_variables={
        "valid_intents": ", ".join(IntentType.values()),
        "intent_definitions": _INTENT_DEFINITIONS,
        "examples": _EXAMPLES,
    },
    template=(
        "You are an intent classifier for a travel and cab booking platform.\n\n"
        "Intent definitions:\n{intent_definitions}\n\n"
        "{examples}\n"
        "Valid intents: {valid_intents}\n\n"
        "Question:\n{question}\n\n"
        "Return JSON only.\n"
        '{{"intent": "PRICING"}}'
    ),
)