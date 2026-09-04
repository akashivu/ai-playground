from __future__ import annotations

from functools import lru_cache

from models.destination_recommendation import DestinationRecommendation
from models.traveler_profile import TravelerProfile
from services.destination_recommendation_engine import (
    DestinationRecommendationEngine,
    get_destination_recommendation_engine,
)
from services.destination_service import (
    DestinationService,
    get_destination_service,
)


class PersonalizedDestinationService:
    """Coordinates destination retrieval and deterministic personalization."""

    def __init__(
        self,
        destination_service: DestinationService,
        recommendation_engine: DestinationRecommendationEngine,
    ) -> None:
        self._destination_service = destination_service
        self._recommendation_engine = recommendation_engine

    def recommend(
        self,
        profile: TravelerProfile,
        *,
        days: int | None = None,
        limit: int = 5,
    ) -> list[DestinationRecommendation]:
        destinations = self._destination_service.get_all()
        return self._recommendation_engine.rank(
            destinations=destinations,
            profile=profile,
            days=days,
            limit=limit,
        )


@lru_cache
def get_personalized_destination_service() -> PersonalizedDestinationService:
    return PersonalizedDestinationService(
        destination_service=get_destination_service(),
        recommendation_engine=get_destination_recommendation_engine(),
    )