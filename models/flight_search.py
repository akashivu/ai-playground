from __future__ import annotations

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: str | None = None
    passengers: int = Field(
        default=1,
        ge=1,
        le=9,
    )
    trip_type: str = "oneway"
    cabin_class: str = "economy"
    currency: str = "INR"