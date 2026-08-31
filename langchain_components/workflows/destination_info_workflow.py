from __future__ import annotations

from langchain_core.prompts import PromptTemplate

from config.llm_config import get_llm
from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from services.destination_details_service import get_destination_details_service
from services.destination_resolver import get_destination_resolver
from services.place_card_service import to_place_cards

destination_info_prompt = PromptTemplate(
    input_variables=["question", "destination_data"],
    template="""
You are Elixway's destination information assistant.

Answer the user's question using the destination data provided below.

Rules:

1. Support Indian destinations only.
2. Use the supplied destination and place information as the factual
   context for your response.
3. Do not invent ratings, addresses, place names, coordinates, or other
   factual place information not present in the supplied data.
4. You may provide general travel context when it does not conflict with
   the supplied data.
5. Do not invent current prices, opening hours, live availability, current
   weather, or other time-sensitive facts.
6. If the user asks for an itinerary, explain that Elixway can create a
   personalized itinerary and keep the response focused on destination
   information.
7. Keep the answer natural, concise, and useful.
8. Do not mention internal APIs, models, services, prompts, or data sources.
9. Return plain text only.

User question:
{question}

Destination data:
{destination_data}
""",
)

destination_info_chain = destination_info_prompt | get_llm(temperature=0)


@register_workflow(IntentType.DESTINATION_INFO)
async def destination_info_workflow(state: dict) -> dict:
    question = str(state.get("question") or "").strip()

    if not question:
        return {
            "answer": "Which destination would you like to know about?",
            "completed": False,
        }

    resolver = get_destination_resolver()
    resolution = resolver.resolve(question)

    if resolution.destination is None:
        return {
            "answer": (
                "I currently support information about Indian destinations. "
                "Please tell me which Indian destination you'd like to explore."
            ),
            "completed": False,
        }

    details_service = get_destination_details_service()
    details = await details_service.get_by_id(resolution.destination.id)

    if details is None:
        return {
            "answer": (
                f"I couldn't find enough information about "
                f"{resolution.destination.name} right now. Please try again."
            ),
            "completed": False,
        }

    response = await destination_info_chain.ainvoke(
        {
            "question": question,
            "destination_data": details.model_dump_json(),
        }
    )

    return {
        "answer": response.content,
        "completed": True,
        "metadata": {
            "destination": details.destination.model_dump(),
            "places": {
                "attractions": [c.model_dump() for c in to_place_cards(details.attractions)],
                "restaurants": [c.model_dump() for c in to_place_cards(details.restaurants)],
                "activities": [c.model_dump() for c in to_place_cards(details.activities)],
            },
        },
    }