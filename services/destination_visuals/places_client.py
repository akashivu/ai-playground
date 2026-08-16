from __future__ import annotations

import logging
from typing import Any

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PHOTO_MEDIA_BASE_URL = "https://places.googleapis.com/v1"


class GooglePlacesClient:
    def __init__(
        self,
        api_key: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        self._timeout = (
            timeout
            if timeout is not None
            else settings.GOOGLE_PLACES_TIMEOUT_SECONDS
        )

    def search_place(
        self,
        query: str,
    ) -> dict[str, Any] | None:
        query = query.strip()

        if not query:
            return None

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress,"
                "places.googleMapsUri,"
                "places.photos"
            ),
        }

        try:
            response = httpx.post(
                TEXT_SEARCH_URL,
                headers=headers,
                json={
                    "textQuery": query,
                    "pageSize": 1,
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.exception(
                "Google Places search failed query=%s",
                query,
            )
            return None

        places = response.json().get("places", [])
        return places[0] if places else None

    def resolve_photo_uri(
        self,
        photo_name: str,
        *,
        max_width_px: int = 1200,
    ) -> str | None:
        if not photo_name:
            return None

        url = (
            f"{PHOTO_MEDIA_BASE_URL}/{photo_name}/media"
        )

        try:
            response = httpx.get(
                url,
                params={
                    "key": self._api_key,
                    "maxWidthPx": max_width_px,
                    "skipHttpRedirect": "true",
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.exception(
                "Google Place Photo request failed photo=%s",
                photo_name,
            )
            return None

        return response.json().get("photoUri")