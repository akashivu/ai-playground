from pydantic import BaseModel


class BookingResult(BaseModel):
    success: bool

    booking_id: int | None = None

    status: str

    message: str

    fare: float | None = None

    distance_km: float | None = None