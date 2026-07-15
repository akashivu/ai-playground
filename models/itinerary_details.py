from pydantic import BaseModel


class ItineraryDetails(BaseModel):
    destination: str
    days: int

    budget: str | None = None
    travelers: int | None = None
    interests: str | None = None