"""
Prompt for an LLM-based EntityExtractor (see entity_extractor.py's
`EntityExtractor` protocol). Not called by the default dictionary-based
implementation — useful once queries start containing entities outside
the fixed dictionary (new cities, new vehicle models, etc.).
"""

ENTITY_SYSTEM_PROMPT = """Extract entities from the user's query for a \
cab-booking assistant. For each entity found, identify its raw text, a \
canonical label (PET, LUGGAGE, REFUND, CANCELLATION, AIRPORT, CITY, \
VEHICLE_TYPE, BOOKING, or a new label if none fit), and a normalized value.

Respond with ONLY a JSON array, no other text:
[{"text": "...", "label": "...", "normalized": "..."}]
If no entities are found, respond with [].
"""


def build_entity_prompt(query: str) -> str:
    return f"{ENTITY_SYSTEM_PROMPT}\n\nQuery: {query!r}"
