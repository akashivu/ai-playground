from pydantic import BaseModel, EmailStr, Field


class BookingConfirmation(BaseModel):
    """
    Canonical booking model used by the AI platform.

    This model represents booking information collected during the
    conversation. It intentionally uses AI-friendly field names.

    Conversion to Spring Boot DTO fields is handled only inside
    SpringBookingClient.
    """

    name: str = Field(
        description="Customer full name",
    )

    email: EmailStr

    mobile: str

    trip_category: str

    trip_type: str

    pickup_location: str

    destination: str

    city: str | None = None

    pickup_address: str | None = None

    travel_date: str

    pickup_time: str

    vehicle_type: str

    distance_km: float = 0.0

    fare: float = 0.0