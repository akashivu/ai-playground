from langchain_core.prompts import PromptTemplate


flight_search_extraction_prompt = PromptTemplate(
    input_variables=[
        "question",
        "current_date",
    ],
    template="""
You extract structured flight-search requirements from a user's request.

Current application date:
{current_date}

User request:
{question}

Rules:

- Extract the departure origin when explicitly provided.
- Extract the arrival destination when explicitly provided.
- Extract the departure date when explicitly provided.
- Resolve relative dates such as "today", "tomorrow",
  "next Friday", etc. using the current application date above.
- Do NOT invent a date when the user did not provide one.
- If the departure date is not provided, return null.
- Extract the return date when explicitly provided.
- If the return date is not provided, return null.
- If a return date is present, trip_type must be "roundtrip".
- Otherwise trip_type must be "oneway".
- Default passengers to 1 when not specified.
- Default cabin_class to "economy".
- Default currency to "INR".
- Do NOT invent an origin.
- Do NOT invent a destination.
- Do NOT invent passenger count.
- Do NOT invent a return date.
- Do NOT add explanations, comments, Markdown, or code fences.
- Return only the structured fields requested by the application.
- Use ISO date format YYYY-MM-DD whenever a date is known.

This extraction step is only for identifying flight-search
requirements. It must never invent missing information.

Examples:

User:
Find flights from Mumbai to Dubai tomorrow

Expected meaning:
origin = Mumbai
destination = Dubai
departure_date = tomorrow resolved relative to current_date
return_date = null
trip_type = oneway

User:
Find a round trip from Delhi to Bangkok from September 5 to September 12

Expected meaning:
origin = Delhi
destination = Bangkok
departure_date = the September 5 date
return_date = the September 12 date
trip_type = roundtrip
"""
)