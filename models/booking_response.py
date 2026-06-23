from pydantic import BaseModel

class BookingResponse(BaseModel):
    answer: str
    booking_details: dict
    completed: bool