from langchain_core.prompts import PromptTemplate


itinerary_prompt = PromptTemplate(
    input_variables=[
        "source",
        "destination",
        "days",
        "budget",
        "travelers",
        "interests",
    ],
    template="""
You are an expert travel planner.

Create a detailed travel itinerary.

Source City:
{source}

Destination:
{destination}

Number of Days:
{days}

Budget:
{budget}

Travelers:
{travelers}

Interests:
{interests}

Generate:

1. Day wise itinerary.
2. Places to visit.
3. Food recommendations.
4. Travel tips.
5. Approximate budget suggestions.

Return plain text.
""",
)