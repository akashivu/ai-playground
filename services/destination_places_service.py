from __future__ import annotations

import logging
from functools import lru_cache

from models.place import Place
from services.google_places_service import (
    GooglePlacesService,
    get_google_places_service,
)
from services.place_cache_service import PlaceCacheService

logger = logging.getLogger(__name__)


class DestinationPlacesService:
    """Retrieves destination-related places.

    Provider calls are cached (with single-flight protection) to
    reduce latency and external API usage. Cache keys are built from
    normalized, structured fields (category, destination, limit) —
    never raw user text — so "Tell me about Coorg", "What are the
    attractions in Coorg?", and "Show me places in Coorg" all resolve
    to the same cache key by the time they reach this service.
    """

    def __init__(self, places_service: GooglePlacesService, cache: PlaceCacheService[list[Place]]) -> None:
        self._places_service = places_service
        self._cache = cache

    @staticmethod
    def _cache_key(category: str, destination_name: str, limit: int) -> str:
        normalized = destination_name.strip().lower()
        return f"places:{category}:{normalized}:{limit}"

    async def _get_places(self, *, category: str, query: str, destination_name: str, limit: int) -> list[Place]:
        key = self._cache_key(category, destination_name, limit)

        async def fetch() -> list[Place]:
            logger.debug("Places cache miss category=%s destination=%s", category, destination_name)
            return await self._places_service.search_places(query, max_results=limit)

        return await self._cache.get_or_set(key, fetch)

    async def get_attractions(self, destination_name: str, *, limit: int = 5) -> list[Place]:
        return await self._get_places(
            category="attractions",
            query=f"top attractions in {destination_name}, India",
            destination_name=destination_name,
            limit=limit,
        )

    async def get_restaurants(self, destination_name: str, *, limit: int = 5) -> list[Place]:
        return await self._get_places(
            category="restaurants",
            query=f"best restaurants in {destination_name}, India",
            destination_name=destination_name,
            limit=limit,
        )

    async def get_activities(self, destination_name: str, *, limit: int = 5) -> list[Place]:
        return await self._get_places(
            category="activities",
            query=f"things to do in {destination_name}, India",
            destination_name=destination_name,
            limit=limit,
        )


@lru_cache(maxsize=1)
def get_destination_places_service() -> DestinationPlacesService:
    return DestinationPlacesService(
        places_service=get_google_places_service(),
        cache=PlaceCacheService[list[Place]](ttl_seconds=3600, max_entries=500),
    )