from pydantic import BaseModel


class BookingConfirmation(BaseModel):
    pickup_location: str
    destination: str
    travel_date: str
    vehicle_type: str