from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.chains.booking_status_chain import booking_status_chain
from services.booking_orchestrator import booking_orchestrator


@register_workflow(IntentType.BOOKING_STATUS)
def booking_status_workflow(state: dict) -> dict:
    """Handles booking status and tracking requests."""
    result = booking_status_chain.invoke({"question": state["question"]})
    booking_id = result.get("booking_id")

    if not booking_id:
        return {"answer": "Please provide your booking ID to check the status."}

    status = booking_orchestrator.get_booking_status(booking_id)

    if status["status"] == "NOT_FOUND":
        return {"answer": f"No booking found with ID '{booking_id}'. Please check and try again."}

    if status["status"] in ("ERROR", "UNKNOWN"):
        return {"answer": f"Unable to fetch status for booking '{booking_id}'. Please contact Elixway support."}

    answer_lines = [
        f"Booking ID: {status['booking_id']}",
        f"Status: {status['status']}",
    ]

    if status.get("pickup_location"):
        answer_lines.append(f"Pickup: {status['pickup_location']}")
    if status.get("destination"):
        answer_lines.append(f"Destination: {status['destination']}")
    if status.get("travel_date"):
        answer_lines.append(f"Date: {status['travel_date']}")

    return {"answer": "\n".join(answer_lines)}