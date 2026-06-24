from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.chains.booking_extraction_chain import booking_extraction_chain
from services.booking_validation_service import find_missing_fields
from services.booking_session_service import booking_session_service
from services.booking_prompt_service import get_next_question
from models.booking_confirmation import BookingConfirmation
from services.booking_orchestrator import booking_orchestrator
from pydantic import ValidationError


@register_workflow(IntentType.BOOKING)
def booking_workflow(state: dict) -> dict:
    """Conversational booking with slot filling and recommendation handoff."""
    previous_booking = state.get("booking_details") or {}
    previous_recommendation = state.get("recommendation_details") or {}
    booking_id = (orchestration_result.get("booking", {}).get("booking_id"))
  
    if (
        previous_recommendation.get("recommended_vehicles")
        and not previous_booking.get("vehicle_type")
    ):
        vehicles = previous_recommendation["recommended_vehicles"]
        if len(vehicles) == 1:
            previous_booking["vehicle_type"] = vehicles[0]

    new_extraction = booking_extraction_chain.invoke({"question": state["question"]})
    merged_booking = booking_session_service.merge_booking(previous_booking, new_extraction)
    missing = find_missing_fields(merged_booking)

    if missing:
        return {
            "answer": get_next_question(missing),
            "booking_details": merged_booking,
            "completed": False,
        }

    try:
        confirmation = BookingConfirmation(**merged_booking)

    except ValidationError:
        return {
        "answer": get_next_question(
            find_missing_fields(merged_booking)
        ),
        "booking_details": merged_booking,
        "completed": False,
    }
    orchestration_result = booking_orchestrator.create_booking(confirmation)

    return {
        "answer": (
            "Booking request received.\n\n"
            f"Booking ID: {booking_id}\n\n"
            f"• Pickup: {confirmation.pickup_location}\n"
            f"• Destination: {confirmation.destination}\n"
            f"• Date: {confirmation.travel_date}\n"
            f"• Vehicle: {confirmation.vehicle_type or 'Not specified'}\n\n"
            "Our team will confirm your booking shortly."
        ),
        "booking_details": merged_booking,
        "booking_confirmation": confirmation.model_dump(),
        
        "completed": True,
    }