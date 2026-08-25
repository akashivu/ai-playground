from __future__ import annotations
from datetime import date
from langchain_components.chains.flight_search_extraction_chain import (
    flight_search_extraction_chain,
)

from langchain_components.registry.workflow_decorator import (
    register_workflow,
)

from langchain_components.routing.intent_types import (
    IntentType,
)

from services.flight_search_session_service import (
    flight_search_session_service,
)


def find_missing_fields(
    request: dict,
) -> list[str]:
    missing: list[str] = []

    if not request.get("origin"):
        missing.append("origin")

    if not request.get("destination"):
        missing.append("destination")

    if not request.get("departure_date"):
        missing.append("departure_date")

    if (
        request.get("trip_type") == "roundtrip"
        and not request.get("return_date")
    ):
        missing.append("return_date")

    return missing


def build_missing_field_question(
    request: dict,
    missing: list[str],
) -> str:
    if "origin" in missing:
        return (
            "Where would you like to fly from?"
        )

    if "destination" in missing:
        return (
            "Where would you like to fly to?"
        )

    if "departure_date" in missing:
        origin = request.get(
            "origin",
            "your departure city",
        )
        destination = request.get(
            "destination",
            "your destination",
        )

        return (
            f"What date would you like to travel "
            f"from {origin} to {destination}?"
        )

    if "return_date" in missing:
        return (
            "What return date would you like "
            "for your round trip?"
        )

    return (
        "Please provide the remaining flight details."
    )


@register_workflow(IntentType.FLIGHT_SEARCH)
def flight_search_workflow(
    state: dict,
) -> dict:
    user_id = str(
        state.get("user_id", "guest")
    )

    session_id = state["session_id"]

    previous = (
        flight_search_session_service.get(
            user_id=user_id,
            session_id=session_id,
        )
    )

    extracted = flight_search_extraction_chain.invoke(
    {
        "question": state["question"],
        "current_date": date.today().isoformat(),
    }
)

    extracted_data = (
        extracted.model_dump()
    )

    merged = (
        flight_search_session_service.merge(
            previous,
            extracted_data,
        )
    )

    missing = find_missing_fields(
        merged
    )

    if missing:
        flight_search_session_service.save(
            user_id=user_id,
            session_id=session_id,
            flight_search=merged,
        )

        return {
            "answer": build_missing_field_question(
                merged,
                missing,
            ),
            "intent": IntentType.FLIGHT_SEARCH,
            "flight_search": {
                "status": "missing_information",
                "request": merged,
                "missing_fields": missing,
            },
            "completed": False,
        }

    flight_search_session_service.save(
        user_id=user_id,
        session_id=session_id,
        flight_search=merged,
    )

    return {
        "answer": (
            f"I found your flight search: "
            f"{merged['origin']} to "
            f"{merged['destination']} on "
            f"{merged['departure_date']}."
        ),
        "intent": IntentType.FLIGHT_SEARCH,
        "flight_search": {
            "status": "ready",
            "request": merged,
            "missing_fields": [],
        },
        "completed": True,
    }