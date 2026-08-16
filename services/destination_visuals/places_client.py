from __future__ import annotations

import logging
from typing import Any

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


PLACES_TEXT_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)

PLACES_PHOTO_BASE_URL = (
    "https://places.googleapis.com/v1/"
)


class GooglePlacesClient:
    """
    Minimal Google Places API (New) client.

    This client is backend-only and never exposes the API key
    to the frontend.
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = (
            api_key
            or settings.GOOGLE_MAPS_API_KEY
        )

        self._timeout = (
            timeout
            if timeout is not None
            else settings.GOOGLE_PLACES_TIMEOUT_SECONDS
        )

    def search_destination(
        self,
        query: str,
    ) -> dict[str, Any] | None:
        if not query.strip():
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

        payload = {
            "textQuery": query.strip(),
            "pageSize": 1,
        }

        try:
            response = httpx.post(
                PLACES_TEXT_SEARCH_URL,
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )

            response.raise_for_status()

        except httpx.HTTPError:
            logger.exception(
                "Google Places search failed query=%s",
                query,
            )
            return None

        data = response.json()

        places = data.get("places", [])

        if not places:
            logger.info(
                "Google Places returned no result query=%s",
                query,
            )
            return None

        return places[0]

    def build_photo_url(
        self,
        photo_name: str,
        *,
        max_width_px: int = 1200,
    ) -> str:
        """
        Returns a Place Photos (New) media endpoint.

        The caller can request this URL from the backend.
        """

        return (
            f"{PLACES_PHOTO_BASE_URL}"
            f"{photo_name}/media"
            f"?maxWidthPx={max_width_px}"
            f"&key={self._api_key}"
        )