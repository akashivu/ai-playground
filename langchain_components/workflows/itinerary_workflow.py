from pydantic import ValidationError

from models.itinerary_details import (
    ItineraryDetails,
)

from langchain_components.registry.workflow_decorator import (
    register_workflow,
)

from langchain_components.routing.intent_types import (
    IntentType,
)

from langchain_components.chains.itinerary_extraction_chain import (
    itinerary_extraction_chain,
)

from langchain_components.chains.itinerary_generation_chain import (
    itinerary_generation_chain,
    itinerary_generation_parser,
)

from services.itinerary_session_service import (
    itinerary_session_service,
)
from langchain_components.workflows import flight_search_workflow

from services.itinerary_validation_service import (
    find_missing_fields,
)

from services.itinerary_prompt_service import (
    get_next_question,
)


@register_workflow(IntentType.ITINERARY)
def itinerary_workflow(
    state: dict,
) -> dict:

    previous = (
        state.get("itinerary_details")
        or {}
    )

    extracted = itinerary_extraction_chain.invoke(
    {
        "question": state["question"]
    }
    )

    
        

    itinerary = (
        itinerary_session_service.merge(
            previous,
            extracted,
        )
    )

    missing = (
        find_missing_fields(
            itinerary,
        )
    )

    if missing:
        return {
            "answer":
                get_next_question(
                    missing,
                ),
            "itinerary_details":
                itinerary,
            "completed":
                False,
        }

    try:
        details = (
            ItineraryDetails(
                **itinerary
            )
        )

    except ValidationError:
        return {
            "answer":
                "Please provide the remaining details.",
            "completed":
                False,
        }

    response = itinerary_generation_chain.invoke(
    {
        **details.model_dump(),
        "format_instructions": (
            itinerary_generation_parser
            .get_format_instructions()
        ),
    }
    )

    return {
    "answer": response.answer_markdown,
    "itinerary_details": itinerary,
    "generated_itinerary": response.model_dump(),
    "completed": True,
}
