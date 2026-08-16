from __future__ import annotations

from pydantic import BaseModel, Field


class PhotoAttribution(BaseModel):
    """
    Attribution information associated with a Google Place photo.
    """

    display_name: str | None = None
    uri: str | None = None


class DestinationVisual(BaseModel):
    """
    Visual information for a destination/place.
    """

    name: str
    place_id: str | None = None
    address: str | None = None
    google_maps_url: str | None = None
    image_url: str | None = None
    attributions: list[PhotoAttribution] = Field(
        default_factory=list
    )


class DestinationVisualResponse(BaseModel):
    """
    Visual enrichment result returned by the service.
    """

    destination: DestinationVisual | None = None