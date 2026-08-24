from langchain_core.prompts import PromptTemplate


flight_search_extraction_prompt = PromptTemplate(
    input_variables=[
        "question",
        "format_instructions",
    ],
    template="""
You extract flight-search requirements from a user's request.

User request:
{question}

Rules:

- Extract the departure origin.
- Extract the arrival destination.
- Extract the departure date.
- If a return date is explicitly given, extract it.
- If the user says "tomorrow", "next Friday", etc.,
  resolve the date using the current system date/context available
  to the application. Do not invent an unrelated date.
- Default passengers to 1 if not specified.
- Default cabin_class to "economy".
- If a return date exists, trip_type must be "roundtrip".
- Otherwise trip_type must be "oneway".
- Do not invent an origin or destination.
- Do not invent a date.
- This parser is only for complete flight-search requests.

Examples:

User: Find flights from Mumbai to Dubai tomorrow
Origin: Mumbai
Destination: Dubai
Trip type: oneway

User: Find a round trip from Delhi to Bangkok from September 5 to September 12
Origin: Delhi
Destination: Bangkok
Trip type: roundtrip

Return:

{format_instructions}
""",
)