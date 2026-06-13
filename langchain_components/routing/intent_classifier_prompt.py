from langchain_core.prompts import PromptTemplate
from langchain_components.routing.intent_types import IntentType

_INTENT_DEFINITIONS = (
    "FAQ: Frequently asked questions about a business, service, pricing, or policies.\n"
    "KNOWLEDGE_SEARCH: Questions requiring retrieval from documents, knowledge base, "
    "uploaded content, guides, or company information.\n"
    "BOOKING: Requests to book, reserve, schedule, or arrange a service.\n"
    "RECOMMENDATION: Requests for suggestions, options, plans, or personalized recommendations.\n"
    "GENERAL: Greetings, casual conversation, or questions not requiring any retrieval."
)

intent_classifier_prompt = PromptTemplate(
    input_variables=["question"],
    partial_variables={
        "valid_intents": ", ".join(IntentType.values()),
        "intent_definitions": _INTENT_DEFINITIONS,
    },
    template=(
        "You are an intent classifier.\n\n"
        "Intent definitions:\n{intent_definitions}\n\n"
        "Valid intents: {valid_intents}\n\n"
        "Question:\n{question}\n\n"
        "Return JSON only.\n"
        'Example: {{"intent": "GENERAL"}}'
    ),
)