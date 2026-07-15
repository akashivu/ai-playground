from pydantic import BaseModel


class ItineraryResponse(BaseModel):
    destination: str
    days: int
    itinerary: str