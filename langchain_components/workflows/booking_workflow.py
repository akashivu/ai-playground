from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.chains.booking_extraction_chain import booking_extraction_chain
from services.booking_validation_service import find_missing_fields
from services.booking_session_service import booking_session_service
from services.booking_prompt_service import get_next_question


@register_workflow(IntentType.BOOKING)
def booking_workflow(state: dict) -> dict:
    """
    Conversational booking workflow with multi-turn slot filling.
    Merges new extraction with existing session booking_details on each turn.
    """
    previous_booking = state.get("booking_details") or {}

    new_extraction = booking_extraction_chain.invoke({"question": state["question"]})

    merged_booking = booking_session_service.merge_booking(previous_booking, new_extraction)

    missing = find_missing_fields(merged_booking)

    if missing:
        return {
            "answer": get_next_question(missing),
            "booking_details": merged_booking,
            "completed": False,
        }

    return {
        "answer": (
            "Booking request received.\n\n"
            f"• Pickup: {merged_booking['pickup_location']}\n"
            f"• Destination: {merged_booking['destination']}\n"
            f"• Date: {merged_booking['travel_date']}\n"
            f"• Vehicle: {merged_booking.get('vehicle_type') or 'Not specified'}\n\n"
            "Our team will confirm your booking shortly."
        ),
        "booking_details": merged_booking,
        "completed": True,
    }