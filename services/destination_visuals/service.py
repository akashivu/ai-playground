from __future__ import annotations

import logging
from typing import Any

from models.generated_itinerary import (
    GeneratedItinerary,
)

from services.destination_visuals.models import (
    DestinationVisualResponse,
    PhotoAttribution,
    PlaceVisual,
    VisualDay,
)
from services.destination_visuals.places_client import (
    GooglePlacesClient,
)

logger = logging.getLogger(__name__)


class DestinationVisualService:
    """
    Best-effort visual enrichment.

    A Google Places failure must never fail itinerary generation.
    """

    def __init__(
        self,
        places_client: GooglePlacesClient | None = None,
    ) -> None:
        self._places_client = (
            places_client or GooglePlacesClient()
        )

    def enrich(
        self,
        destination: str,
        itinerary: GeneratedItinerary,
    ) -> DestinationVisualResponse:

        destination_visual = self._resolve_place(
            destination
        )

        visual_days: list[VisualDay] = []

        for day in itinerary.days:
            places: list[PlaceVisual] = []

            for itinerary_place in day.places:
                visual = self._resolve_place(
                    itinerary_place.name,
                    destination=destination,
                )

                if visual:
                    places.append(visual)

            visual_days.append(
                VisualDay(
                    day=day.day,
                    title=day.title,
                    places=places,
                )
            )

        return DestinationVisualResponse(
            destination=destination_visual,
            days=visual_days,
        )

    def _resolve_place(
        self,
        name: str,
        destination: str | None = None,
    ) -> PlaceVisual | None:

        query = name

        if destination:
            query = f"{name}, {destination}"

        place = self._places_client.search_place(query)

        if not place:
            return None

        display_name = (
            place.get("displayName", {}).get(
                "text"
            )
            or name
        )

        photos = place.get("photos", [])
        first_photo = photos[0] if photos else {}

        image_url = None

        photo_name = first_photo.get("name")
        if photo_name:
            image_url = (
                self._places_client.resolve_photo_uri(
                    photo_name
                )
            )

        attributions: list[PhotoAttribution] = []

        for attribution in first_photo.get(
            "authorAttributions",
            [],
        ):
            attributions.append(
                PhotoAttribution(
                    display_name=attribution.get(
                        "displayName"
                    ),
                    uri=attribution.get("uri"),
                )
            )

        return PlaceVisual(
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


destination_visual_service = DestinationVisualService()