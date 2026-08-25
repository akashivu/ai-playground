from __future__ import annotations

from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    """
    Structured flight-search extraction result.

    Missing information stays None so the workflow can ask
    the user for the missing fields instead of inventing values.
    """

    origin: str | None = None
    destination: str | None = None

    departure_date: str | None = None
    return_date: str | None = None

    passengers: int = Field(
        default=1,
        ge=1,
        le=9,
    )

    trip_type: str = "oneway"
    cabin_class: str = "economy"
    currency: str = "INR"