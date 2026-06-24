import os
import httpx
from utils.logger import logger
from models.booking_confirmation import BookingConfirmation


class BookingOrchestrator:
    """
    Orchestrates the booking lifecycle.
    Currently returns structured confirmation.
    Wire to AdiyogiCabz booking API when ready.
    """

    def __init__(self) -> None:
        self.api_url = os.getenv("ADIYOGICABZ_API_URL")
        self.api_key = os.getenv("ADIYOGICABZ_API_KEY")

    def create_booking(self, confirmation: BookingConfirmation) -> dict:
        """Creates a booking. Returns structured confirmation object."""
        logger.info(
            f"Booking request: {confirmation.pickup_location} → "
            f"{confirmation.destination} on {confirmation.travel_date}"
        )

        if self.api_url and self.api_key:
            return self._create_via_api(confirmation)

        return self._create_local(confirmation)

    def _create_local(self, confirmation: BookingConfirmation) -> dict:
        """Returns structured booking data without API call. Used until API is ready."""
        return {
            "status": "pending",
            "message": "Booking received. Our team will confirm shortly.",
            "booking": confirmation.model_dump(),
        }

    def _create_via_api(self, confirmation: BookingConfirmation) -> dict:
        """Posts booking to AdiyogiCabz backend API."""
        try:
            response = httpx.post(
                f"{self.api_url}/api/bookings",
                json=confirmation.model_dump(),
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.error("AdiyogiCabz API timeout during booking creation.")
            return self._create_local(confirmation)

        except httpx.HTTPStatusError as e:
            logger.error(f"AdiyogiCabz API error: {e.response.status_code}")
            return self._create_local(confirmation)

        except Exception as e:
            logger.exception(f"Unexpected error during booking creation: {e}")
            return self._create_local(confirmation)

    def get_booking_status(self, booking_id: str) -> dict:
        """Returns booking status from API or local fallback."""
        logger.info(f"Fetching status for booking: {booking_id}")

        if self.api_url and self.api_key:
            return self._get_status_via_api(booking_id)

        return {
            "booking_id": booking_id,
            "status": "PENDING",
            "message": "Status check unavailable. Please contact AdiyogiCabz support.",
        }

    def _get_status_via_api(self, booking_id: str) -> dict:
        """Fetches booking status from AdiyogiCabz backend."""
        try:
            response = httpx.get(
                f"{self.api_url}/api/bookings/{booking_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.error(
                f"API timeout fetching status for booking: {booking_id}"
            )
            return {
                "booking_id": booking_id,
                "status": "UNKNOWN",
                "message": "Request timed out.",
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {
                    "booking_id": booking_id,
                    "status": "NOT_FOUND",
                    "message": "Booking not found.",
                }

            logger.error(
                f"API error fetching booking status: "
                f"{e.response.status_code}"
            )
            return {
                "booking_id": booking_id,
                "status": "ERROR",
                "message": "Unable to fetch status.",
            }

        except Exception as e:
            logger.exception(
                f"Unexpected error fetching booking status: {e}"
            )
            return {
                "booking_id": booking_id,
                "status": "ERROR",
                "message": "Unable to fetch status.",
            }


booking_orchestrator = BookingOrchestrator()