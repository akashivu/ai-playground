from __future__ import annotations

from pydantic import BaseModel


class PlaceCard(BaseModel):
    """Frontend-facing representation of a place.

    Deliberately decoupled from Place/Google — the React UI should
    never need to know a photo came from Google Places or that
    photo_url is actually a route on our own backend.
    """

    place_id: str
    name: str

    address: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    rating: float | None = None
    user_ratings_total: int | None = None

    photo_url: str | None = None
    category: str | None = None
    website: str | None = None

    model_config = {"frozen": True}