from pydantic import ValidationError
from auth.schemas import CurrentUser
from langchain_components.chains.booking_extraction_chain import booking_extraction_chain
from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from models.booking_confirmation import BookingConfirmation
from models.booking_result import BookingResult
from services.booking_orchestrator import booking_orchestrator
from services.booking_prompt_service import get_next_question
from services.booking_session_service import booking_session_service
from services.booking_validation_service import find_missing_fields


@register_workflow(IntentType.BOOKING)
def booking_workflow(state: dict) -> dict:
    """
    Conversational booking workflow with slot filling.
    """
    current_user: CurrentUser | None = state.get("current_user")
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    previous_booking = state.get("booking_details") or {}
    previous_recommendation = state.get("recommendation_details") or {}

    #
    # Auto-select vehicle if recommendation returned only one.
    #
    if (
        previous_recommendation.get("recommended_vehicles")
        and not previous_booking.get("vehicle_type")
    ):
        vehicles = previous_recommendation["recommended_vehicles"]
        if len(vehicles) == 1:
            previous_booking["vehicle_type"] = vehicles[0]

    #
    # Extract booking information.
    #
    extracted = booking_extraction_chain.invoke({"question": state["question"]})
    merged_booking = booking_session_service.merge_booking(previous_booking, extracted)

    #
    # Check missing fields.
    #
    missing = find_missing_fields(merged_booking)
    if missing:
        return {
            "answer": get_next_question(missing),
            "booking_details": merged_booking,
            "completed": False,
        }

    #
    # Validate booking model.
    #
    try:
        confirmation = BookingConfirmation(**merged_booking)
    except ValidationError:
        return {
            "answer": get_next_question(find_missing_fields(merged_booking)),
            "booking_details": merged_booking,
            "completed": False,
        }

    #
    # Create booking.
    #
    result: BookingResult = booking_orchestrator.create_booking(
        confirmation=confirmation,
        current_user=current_user,
    )

    #
    # Booking failed.
    #
    if not result.success:
        return {
            "answer": result.message,
            "booking_details": merged_booking,
            "completed": False,
        }

    #
    # Booking successful.
    #
    answer = (
        "Your booking has been confirmed.\n\n"
        f"Booking ID: ADY-{result.booking_id}\n\n"
        f"Pickup: {confirmation.pickup_location}\n"
        f"Destination: {confirmation.destination}\n"
        f"Travel Date: {confirmation.travel_date}\n"
        f"Vehicle: {confirmation.vehicle_type}\n"
        f"Distance: {result.distance_km:.1f} km\n"
        f"Estimated Fare: ₹{result.fare:.2f}\n\n"
        "A confirmation email has been sent to your registered email address."
    )

    return {
        "answer": answer,
        "booking_details": merged_booking,
        "booking_confirmation": confirmation.model_dump(),
        "orchestration_result": result.model_dump(),
        "completed": True,
    }