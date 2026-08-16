from langchain_core.prompts import PromptTemplate


itinerary_generation_prompt = PromptTemplate(
    input_variables=[
        "destination",
        "days",
        "budget",
        "travelers",
        "interests",
        "format_instructions",
    ],
    template="""
You are an expert travel planner for Elixway.

Create a detailed, practical itinerary.

Destination:
{destination}

Days:
{days}

Budget:
{budget}

Travelers:
{travelers}

Interests:
{interests}

Generate:

1. A polished markdown itinerary suitable for displaying directly
   to the user.
2. A structured day-by-day list of the important places mentioned
   in the itinerary.

Rules for structured places:
- Include real, specific destinations, attractions, landmarks,
  beaches, museums, markets, temples, parks, etc.
- Do not include hotels, generic areas, restaurants, transport
  providers, or generic activities unless they are clearly a
  destination/attraction.
- Keep the place name concise and searchable.
- Assign each place to the correct day.
- Use periods such as "morning", "afternoon", or "evening"
  when applicable.
- Do not invent fake place names.

The markdown answer should include:
- day-wise itinerary
- activities
- food recommendations
- approximate budget
- local tips

Return the result using exactly this structure:

{format_instructions}
""",
)