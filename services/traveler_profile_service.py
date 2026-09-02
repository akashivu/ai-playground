from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Protocol

from models.traveler_profile import TravelerProfile


class TravelerProfileRepository(Protocol):
    

    async def get(self, user_id: str) -> TravelerProfile: ...
    async def save(self, user_id: str, profile: TravelerProfile) -> TravelerProfile: ...


class InMemoryTravelerProfileRepository:
    

    def __init__(self) -> None:
        self._profiles: dict[str, TravelerProfile] = {}
        self._lock = asyncio.Lock()

    async def get(self, user_id: str) -> TravelerProfile:
        async with self._lock:
            return self._profiles.get(str(user_id), TravelerProfile())

    async def save(self, user_id: str, profile: TravelerProfile) -> TravelerProfile:
        async with self._lock:
            self._profiles[str(user_id)] = profile
        return profile


class TravelerProfileService:
    """Application-facing entry point for persistent traveler preferences."""

    def __init__(self, repository: TravelerProfileRepository) -> None:
        self._repository = repository

    async def get(self, user_id: str) -> TravelerProfile:
        return await self._repository.get(user_id)

    async def save(self, user_id: str, profile: TravelerProfile) -> TravelerProfile:
        return await self._repository.save(user_id, profile)

    async def update(self, user_id: str, **updates) -> TravelerProfile:
        """Generic field-overwrite update — NOT list-merging.

        For merging LLM-extracted preferences into a profile, use
        TravelerPreferenceService.update_from_extraction instead; this
        method replaces whichever fields you pass, it doesn't append.
        """
        current = await self.get(user_id)
        data = current.model_dump()

        for key, value in updates.items():
            if value is not None:
                data[key] = value

        updated = TravelerProfile.model_validate(data)
        return await self.save(user_id, updated)


@lru_cache
def get_traveler_profile_service() -> TravelerProfileService:
    """FastAPI dependency — one shared instance per process."""
    return TravelerProfileService(repository=InMemoryTravelerProfileRepository())