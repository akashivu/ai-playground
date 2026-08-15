"""
Prompt for an LLM-based IntentClassifier (see intent_classifier.py's
`IntentClassifier` protocol). Not called by the default rule-based
implementation — wire this into a real LLM call when the keyword
approach stops being precise enough.
"""

INTENT_SYSTEM_PROMPT = """You classify a user's query into exactly one intent \
for a cab-booking assistant's knowledge retrieval system.

Valid intents: FAQ, BOOKING, POLICY, CITY, VEHICLE, PRICING, GENERAL

Respond with ONLY a JSON object, no other text:
{"intent": "<ONE_OF_THE_VALID_INTENTS>", "confidence": <float 0-1>}
"""


def build_intent_prompt(query: str) -> str:
    return f"{INTENT_SYSTEM_PROMPT}\n\nQuery: {query!r}"
