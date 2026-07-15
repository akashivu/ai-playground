from langchain_core.prompts import PromptTemplate


itinerary_generation_prompt = PromptTemplate(
    input_variables=[
        "destination",
        "days",
        "budget",
        "travelers",
        "interests",
    ],
    template="""
You are an expert travel planner.

Create a detailed itinerary.

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

1. Day wise itinerary.
2. Places to visit.
3. Food recommendations.
4. Approximate budget.
5. Local tips.

Return plain text.
""",
)