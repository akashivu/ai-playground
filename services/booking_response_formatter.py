from models.booking_api_models import SpringBookingResponse
from models.booking_confirmation import BookingConfirmation


class BookingResponseFormatter:
    """Formats booking results into user-facing answer strings."""

    def confirmed(self, response: SpringBookingResponse) -> str:
        lines = [
            "Booking confirmed! ✓\n",
            f"• Reference: ADY-{response.booking_id}",
            f"• Status: {response.status}",
        ]
        if response.from_location:
            lines.append(f"• Pickup: {response.from_location}")
        if response.to_location:
            lines.append(f"• Destination: {response.to_location}")
        if response.pickup_date:
            lines.append(f"• Date: {response.pickup_date}")
        if response.vehicle_name:
            lines.append(f"• Vehicle: {response.vehicle_name}")
        if response.fare:
            lines.append(f"• Fare: ₹{response.fare:.0f}")
        lines.append("\nA confirmation email has been sent. Thank you for choosing Elixway!")
        return "\n".join(lines)

    def pending(self, confirmation: BookingConfirmation) -> str:
        return (
            "Booking request received.\n\n"
            f"• Pickup: {confirmation.pickup_location}\n"
            f"• Destination: {confirmation.destination}\n"
            f"• Date: {confirmation.travel_date}\n"
            f"• Vehicle: {confirmation.vehicle_type or 'Not specified'}\n\n"
            "Our team will confirm your booking shortly."
        )


booking_response_formatter = BookingResponseFormatter()