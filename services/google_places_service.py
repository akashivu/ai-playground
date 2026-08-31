from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import httpx

from config.settings import settings
from models.place import Place

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """Server-side integration with Google Places.

    Responsible only for talking to Google and translating provider
    responses into application models — no query construction, no
    caching, no destination logic. That lives one layer up in
    DestinationPlacesService.
    """

    SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

    _FIELD_MASK = (
        "places.id,"
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.rating,"
        "places.userRatingCount,"
        "places.types,"
        "places.websiteUri,"
        "places.nationalPhoneNumber,"
        "places.photos"
    )

    def __init__(self, api_key: str, timeout_seconds: float = 8.0) -> None:
        if not api_key:
            raise ValueError("Google Maps API key is not configured")

        self._api_key = api_key
        self._timeout = timeout_seconds

    async def search_places(self, query: str, *, max_results: int = 5) -> list[Place]:
        query = query.strip()

        if not query or max_results <= 0:
            return []

        max_results = min(max_results, 20)

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": self._FIELD_MASK,
        }
        payload = {"textQuery": query, "pageSize": max_results}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self.SEARCH_URL, headers=headers, json=payload)
            response.raise_for_status()

        except httpx.TimeoutException:
            logger.warning("Google Places timeout query=%r", query)
            return []

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Google Places HTTP error query=%r status=%s",
                query,
                exc.response.status_code,
            )
            return []

        except httpx.HTTPError:
            logger.exception("Google Places request failed query=%r", query)
            return []

        try:
            data = response.json()
        except ValueError:
            logger.exception("Google Places returned invalid JSON query=%r", query)
            return []

        return self._parse_places(data.get("places", []))

    @staticmethod
    def _parse_places(raw_places: list[dict[str, Any]]) -> list[Place]:
        places: list[Place] = []

        for raw in raw_places:
            try:
                display_name = raw.get("displayName") or {}
                location = raw.get("location") or {}

                photos = raw.get("photos") or []
                first_photo = photos[0] if photos else None
                photo_resource_name = (
                    first_photo.get("name") if isinstance(first_photo, dict) else None
                )

                place = Place(
                    place_id=str(raw.get("id", "")),
                    name=str(display_name.get("text", "")).strip(),
                    address=raw.get("formattedAddress"),
                    latitude=location.get("latitude"),
                    longitude=location.get("longitude"),
                    rating=raw.get("rating"),
                    user_ratings_total=raw.get("userRatingCount"),
                    types=raw.get("types") or [],
                    website=raw.get("websiteUri"),
                    phone_number=raw.get("nationalPhoneNumber"),
                    photo_resource_name=photo_resource_name,
                )

                if not place.place_id or not place.name:
                    continue

                places.append(place)

            except Exception:
                logger.exception("Failed to parse Google Place")

        return places


@lru_cache
def get_google_places_service() -> GooglePlacesService:
    """FastAPI dependency — one shared instance per process.

    Deliberately lazy: importing this module must never require a
    configured API key. The key is only needed the first time this
    is actually called.
    """
    return GooglePlacesService(api_key=settings.GOOGLE_MAPS_API_KEY)