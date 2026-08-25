from __future__ import annotations

import re

from langchain_components.registry.workflow_decorator import (
    register_workflow,
)

from langchain_components.routing.intent_types import (
    IntentType,
)

from langchain_components.chains.recommendation_extraction_chain import (
    recommendation_extraction_chain,
)

from services.vehicle_recommendation_service import (
    recommend_vehicles,
    format_recommendations,
)

from services.destination_recommendation_service import (
    destination_recommendation_service,
)


VEHICLE_TERMS = frozenset(
    {
        "vehicle",
        "vehicles",
        "car",
        "cars",
        "cab",
        "cabs",
        "taxi",
        "suv",
        "sedan",
        "innova",
        "traveller",
        "traveler",
        "bus",
        "minivan",
        "ride",
        "rides",
        "passenger",
        "passengers",
        "luggage",
    }
)


def _tokenize(question: str) -> set[str]:
    return set(
        re.findall(
            r"[a-z0-9]+",
            question.lower(),
        )
    )


def _is_vehicle_recommendation(
    question: str,
) -> bool:
    tokens = _tokenize(question)

    return bool(
        tokens.intersection(
            VEHICLE_TERMS
        )
    )


@register_workflow(IntentType.RECOMMENDATION)
def recommendation_workflow(
    state: dict,
) -> dict:
    """
    Handles two recommendation modes:

    1. Vehicle recommendation:
       Uses the existing vehicle recommendation system.

    2. Destination recommendation:
       Uses the temporary India-only LLM recommendation service.
    """

    question = (
        str(
            state.get("question")
            or ""
        ).strip()
    )

    if not question:
        return {
            "answer": (
                "What would you like a recommendation for?"
            ),
            "completed": False,
        }

    # ---------------------------------------------------------
    # VEHICLE RECOMMENDATION
    # ---------------------------------------------------------

    if _is_vehicle_recommendation(
        question
    ):
        details = (
            recommendation_extraction_chain.invoke(
                {
                    "question": question,
                }
            )
        )

        raw_passengers = details.get(
            "passengers"
        )

        if raw_passengers is None:
            return {
                "answer": (
                    "How many passengers will be travelling?"
                ),
                "completed": False,
                "recommendation_details": {
                    "type": "vehicle",
                },
            }

        try:
            passengers = int(
                raw_passengers
            )

        except (
            ValueError,
            TypeError,
        ):
            return {
                "answer": (
                    "Could you tell me the number of passengers "
                    "as a number? For example: 4, 7, or 12."
                ),
                "completed": False,
                "recommendation_details": {
                    "type": "vehicle",
                },
            }

        if passengers <= 0:
            return {
                "answer": (
                    "Please provide a valid number of passengers."
                ),
                "completed": False,
                "recommendation_details": {
                    "type": "vehicle",
                },
            }

        vehicles = recommend_vehicles(
            passengers
        )

        answer = format_recommendations(
            vehicles
        )

        return {
            "answer": answer,
            "completed": True,
            "recommendation_details": {
                "type": "vehicle",
                "passengers": passengers,
                "trip_type": details.get(
                    "trip_type"
                ),
                "needs_luggage": details.get(
                    "needs_luggage"
                ),
                "recommended_vehicles": [
                    vehicle["name"]
                    for vehicle in vehicles
                ],
            },
        }

    # ---------------------------------------------------------
    # DESTINATION RECOMMENDATION
    # ---------------------------------------------------------

    answer = (
        destination_recommendation_service.recommend(
            question
        )
    )

    return {
        "answer": answer,
        "completed": True,
        "recommendation_details": {
            "type": "destination",
        },
    }