from pydantic import BaseModel


class BookingStatus(BaseModel):
    booking_id: str
    status: str
    pickup_location: str | None = None
    destination: str | None = None
    travel_date: str | None = None