from utils.logger import logger
from auth.schemas import CurrentUser
from clients.spring_booking_client import spring_booking_client
from models.booking_confirmation import BookingConfirmation
from models.booking_result import BookingResult


class BookingOrchestrator:
    """
    Coordinates the complete booking lifecycle.
    """

    def create_booking(
        self,
        confirmation: BookingConfirmation,
        current_user: CurrentUser | None = None,
    ) -> BookingResult:
        logger.info(
            "Booking request: %s -> %s",
            confirmation.pickup_location,
            confirmation.destination,
        )

        estimate = spring_booking_client.estimate_fare(
            pickup=confirmation.pickup_location,
            destination=confirmation.destination,
            current_user=current_user,
        )

        if estimate:
            confirmation.distance_km = estimate.get("distanceKm", 0)
            confirmation.fare = estimate.get("fare", 0)

        response = spring_booking_client.confirm_booking(
            confirmation=confirmation,
            current_user=current_user,
        )

        if response is None:
            return BookingResult(
                success=False,
                status="FAILED",
                message="Unable to create booking at the moment.",
                fare=confirmation.fare,
                distance_km=confirmation.distance_km,
            )

        return BookingResult(
            success=True,
            booking_id=response.booking_id,
            status=response.status,
            message="Booking confirmed successfully.",
            fare=response.fare,
            distance_km=response.distance_km,
        )

    def get_booking_status(
        self,
        booking_id: int,
        current_user: CurrentUser | None = None,
    ) -> BookingResult:
        response = spring_booking_client.get_booking_status(
            booking_id=booking_id,
            current_user=current_user,
        )

        if response is None:
            return BookingResult(
                success=False,
                booking_id=booking_id,
                status="NOT_FOUND",
                message="Booking not found.",
            )

        return BookingResult(
            success=True,
            booking_id=response.booking_id,
            status=response.status,
            message="Booking status retrieved.",
            fare=response.fare,
        )


booking_orchestrator = BookingOrchestrator()