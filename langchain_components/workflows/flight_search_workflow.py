from __future__ import annotations

from langchain_components.chains.flight_search_extraction_chain import (
    flight_search_extraction_chain,
    flight_search_parser,
)

from langchain_components.registry.workflow_decorator import (
    register_workflow,
)

from langchain_components.routing.intent_types import IntentType


@register_workflow(IntentType.FLIGHT_SEARCH)
def flight_search_workflow(
    state: dict,
) -> dict:
    question = state["question"]

    request = flight_search_extraction_chain.invoke(
        {
            "question": question,
            "format_instructions": (
                flight_search_parser
                .get_format_instructions()
            ),
        }
    )

    return {
        "answer": (
            f"I found your flight search request: "
            f"{request.origin} to "
            f"{request.destination}."
        ),
        "flight_search": {
            "status": "ready",
            "request": request.model_dump(),
        },
        "completed": True,
    }