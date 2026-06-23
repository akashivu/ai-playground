from pydantic import BaseModel


class BookingRequest(BaseModel):
    pickup_location: str | None = None
    destination: str | None = None
    travel_date: str | None = None
    vehicle_type: str | None = None