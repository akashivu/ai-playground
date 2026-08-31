from __future__ import annotations

from models.place import Place
from models.place_card import PlaceCard
from services.place_photo_service import get_place_photo_service


def to_place_card(place: Place) -> PlaceCard:
    photo_service = get_place_photo_service()

    return PlaceCard(
        place_id=place.place_id,
        name=place.name,
        address=place.address,
        latitude=place.latitude,
        longitude=place.longitude,
        rating=place.rating,
        user_ratings_total=place.user_ratings_total,
        photo_url=photo_service.get_public_photo_path(place.photo_resource_name),
        category=place.types[0] if place.types else None,
        website=place.website,
    )


def to_place_cards(places: list[Place]) -> list[PlaceCard]:
    return [to_place_card(p) for p in places]