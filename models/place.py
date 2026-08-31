from __future__ import annotations

from pydantic import BaseModel, Field


class Place(BaseModel):
    """Canonical, provider-neutral representation of a place.

    Internal model only — never returned directly to the frontend.
    See PlaceCard for the public-facing shape.
    """

    place_id: str
    name: str

    address: str | None = None

    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    rating: float | None = Field(default=None, ge=0, le=5)
    user_ratings_total: int | None = Field(default=None, ge=0)

    types: list[str] = Field(default_factory=list)

    website: str | None = None
    phone_number: str | None = None

    # Google's internal photo resource identifier — NOT a URL, and
    # never sent to the frontend. Resolved into PlaceCard.photo_url
    # (a proxied, key-free URL) at the response boundary.
    photo_resource_name: str | None = None

    model_config = {"frozen": True}