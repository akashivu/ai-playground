from __future__ import annotations

from pydantic import BaseModel, Field


class PhotoAttribution(BaseModel):
    display_name: str | None = None
    uri: str | None = None


class PlaceVisual(BaseModel):
    name: str
    place_id: str | None = None
    address: str | None = None
    google_maps_url: str | None = None
    image_url: str | None = None
    attributions: list[PhotoAttribution] = Field(
        default_factory=list
    )


class VisualDay(BaseModel):
    day: int
    title: str
    places: list[PlaceVisual] = Field(
        default_factory=list
    )


class DestinationVisualResponse(BaseModel):
    destination: PlaceVisual | None = None
    days: list[VisualDay] = Field(
        default_factory=list
    )