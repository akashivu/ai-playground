from __future__ import annotations

from functools import lru_cache
from urllib.parse import quote

from config.settings import settings


class PlacePhotoService:
    """Resolves Google photo resources into URLs.

    get_google_photo_url embeds the API key and must NEVER be sent to
    a client — it exists only for our own backend's photo-proxy route
    to call Google with. get_public_photo_path is the only one safe
    to put in a PlaceCard.
    """

    _GOOGLE_BASE_URL = "https://places.googleapis.com/v1/"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Google Maps API key is not configured")
        self._api_key = api_key

    def get_google_photo_url(self, photo_resource_name: str, *, max_width: int) -> str:
        """Server-side only. Never expose this to the frontend."""
        return (
            f"{self._GOOGLE_BASE_URL}{photo_resource_name}/media"
            f"?maxWidthPx={max_width}&key={self._api_key}"
        )

    def get_public_photo_path(self, photo_resource_name: str | None, *, max_width: int = 800) -> str | None:
        """Frontend-safe. Points at our own backend; no API key present."""
        if not photo_resource_name:
            return None
        if max_width <= 0:
            raise ValueError("max_width must be greater than zero")

        encoded_name = quote(photo_resource_name, safe="")
        return f"/api/places/photo?name={encoded_name}&max_width={max_width}"


@lru_cache
def get_place_photo_service() -> PlacePhotoService:
    return PlacePhotoService(api_key=settings.GOOGLE_MAPS_API_KEY)