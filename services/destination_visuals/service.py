from __future__ import annotations

import logging

from services.destination_visuals.models import (
    DestinationVisual,
    DestinationVisualResponse,
    PhotoAttribution,
)
from services.destination_visuals.places_client import (
    GooglePlacesClient,
)

logger = logging.getLogger(__name__)


class DestinationVisualService:
    """
    Enriches itinerary destinations with Google Place visuals.

    Visual enrichment is best-effort:
    a failure here must never break itinerary generation.
    """

    def __init__(
        self,
        places_client: GooglePlacesClient | None = None,
    ) -> None:
        self._places_client = (
            places_client
            or GooglePlacesClient()
        )

    def enrich_destination(
        self,
        destination: str,
    ) -> DestinationVisualResponse:
        if not destination.strip():
            return DestinationVisualResponse()

        place = self._places_client.search_destination(
            f"{destination}, India"
        )

        if not place:
            return DestinationVisualResponse()

        display_name = place.get(
            "displayName",
            {},
        ).get(
            "text",
            destination,
        )

        photos = place.get(
            "photos",
            [],
        )

        image_url: str | None = None
        attributions: list[PhotoAttribution] = []

        if photos:
            first_photo = photos[0]

            photo_name = first_photo.get(
                "name"
            )

            if photo_name:
                image_url = (
                    self._places_client.build_photo_url(
                        photo_name
                    )
                )

            for attribution in first_photo.get(
                "authorAttributions",
                [],
            ):
                attributions.append(
                    PhotoAttribution(
                        display_name=(
                            attribution.get(
                                "displayName"
                            )
                        ),
                        uri=(
                            attribution.get(
                                "uri"
                            )
                        ),
                    )
                )

        return DestinationVisualResponse(
            destination=DestinationVisual(
                name=display_name,
                place_id=place.get("id"),
                address=place.get(
                    "formattedAddress"
                ),
                google_maps_url=place.get(
                    "googleMapsUri"
                ),
                image_url=image_url,
                attributions=attributions,
            )
        )


destination_visual_service = (
    DestinationVisualService()
)