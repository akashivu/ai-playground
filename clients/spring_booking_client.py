import os
import httpx

from utils.logger import logger
from auth.schemas import CurrentUser
from models.booking_confirmation import BookingConfirmation
from models.booking_api_models import (
    SpringBookingRequest,
    SpringBookingResponse,
    SpringBookingStatusResponse,
)


class SpringBookingClient:
    """
    Client responsible for communicating with the
    AdiyogiCabz Spring Boot backend.

    This is the ONLY place that knows about the
    Spring Boot DTO field names.
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("ADIYOGICABZ_API_URL", "")
        self.timeout = 10.0

    def _is_configured(self) -> bool:
        return bool(self.base_url)

    def _headers(self, current_user: CurrentUser | None = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if current_user and current_user.jwt_token:
            headers["Authorization"] = f"Bearer {current_user.jwt_token}"
        return headers

    def estimate_fare(
        self,
        pickup: str,
        destination: str,
        current_user: CurrentUser | None = None,
    ) -> dict | None:
        """
        Calls Spring Boot fare estimation endpoint.
        """
        if not self._is_configured():
            return None

        try:
            response = httpx.post(
                f"{self.base_url}/api/bookings/estimate",
                json={"pickup": pickup, "dropoff": destination},
                headers=self._headers(current_user),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.exception(f"Estimate API failed: {e}")
            return None

    def confirm_booking(
        self,
        confirmation: BookingConfirmation,
        current_user: CurrentUser | None = None,
    ) -> SpringBookingResponse | None:
        """
        Sends booking confirmation to Spring Boot.
        """
        if not self._is_configured():
            return None

        try:
            request = SpringBookingRequest(
                name=confirmation.name,
                email=confirmation.email,
                mobile=confirmation.mobile,
                trip_category=confirmation.trip_category,
                trip_type=confirmation.trip_type,
                from_location=confirmation.pickup_location,
                to_location=confirmation.destination,
                city=confirmation.city,
                pickup_location=confirmation.pickup_address,
                pickup_date=confirmation.travel_date,
                pickup_time=confirmation.pickup_time,
                vehicle_name=confirmation.vehicle_type,
                distance_km=confirmation.distance_km,
                fare=confirmation.fare,
            )

            response = httpx.post(
                f"{self.base_url}/api/bookings/confirm",
                json=request.model_dump(by_alias=True),
                headers=self._headers(current_user),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return SpringBookingResponse.model_validate(response.json())

        except httpx.TimeoutException:
            logger.error("Booking confirmation timeout.")
            return None

        except httpx.HTTPStatusError as e:
            logger.error(f"Booking API error: {e.response.status_code}")
            return None

        except Exception as e:
            logger.exception(f"Unexpected booking error: {e}")
            return None

    def get_booking_status(
        self,
        booking_id: int,
        current_user: CurrentUser | None = None,
    ) -> SpringBookingStatusResponse | None:
        """
        Returns booking status.
        """
        if not self._is_configured():
            return None

        try:
            response = httpx.get(
                f"{self.base_url}/api/bookings/{booking_id}",
                headers=self._headers(current_user),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return SpringBookingStatusResponse.model_validate(response.json())

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Status API error: {e.response.status_code}")
            return None

        except Exception as e:
            logger.exception(f"Status lookup failed: {e}")
            return None


spring_booking_client = SpringBookingClient()