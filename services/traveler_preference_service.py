from __future__ import annotations

from functools import lru_cache

from models.traveler_preference_update import TravelerPreferenceUpdate
from models.traveler_profile import TravelerProfile
from services.traveler_profile_service import (
    TravelerProfileService,
    get_traveler_profile_service,
)


class TravelerPreferenceService:
    

    def __init__(self, profile_service: TravelerProfileService) -> None:
        self._profile_service = profile_service

    async def update_from_extraction(self, user_id: str, extracted: dict) -> TravelerProfile:
        current = await self._profile_service.get(user_id)
        update = TravelerPreferenceUpdate.model_validate(extracted)

        data = current.model_dump()

        data["interests"] = self._merge_lists(data["interests"], update.interests)
        data["travel_styles"] = self._merge_lists(data["travel_styles"], update.travel_styles)
        data["traveling_with"] = self._merge_lists(data["traveling_with"], update.traveling_with)
        data["favorite_destinations"] = self._merge_lists(
            data["favorite_destinations"], update.favorite_destinations
        )
        data["avoided_preferences"] = self._merge_lists(
            data["avoided_preferences"], update.avoided_preferences
        )

        if update.preferred_pace:
            data["preferred_pace"] = update.preferred_pace

        if update.budget_level:
            data["budget_level"] = update.budget_level

        updated = TravelerProfile.model_validate(data)
        return await self._profile_service.save(user_id, updated)

    @staticmethod
    def _merge_lists(existing: list[str], new_values: list[str]) -> list[str]:
        result = list(existing)
        for value in new_values:
            normalized = value.strip().lower()
            if normalized and normalized not in result:
                result.append(normalized)
        return result


@lru_cache
def get_traveler_preference_service() -> TravelerPreferenceService:
    return TravelerPreferenceService(profile_service=get_traveler_profile_service())