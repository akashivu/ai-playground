from pydantic import BaseModel


class ItineraryRequest(BaseModel):
    source: str | None = None
    destination: str
    days: int
    budget: str | None = None
    travelers: int | None = None
    interests: list[str] = []