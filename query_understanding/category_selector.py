
from __future__ import annotations

_INTENT_TO_CATEGORY = {
    "POLICY": "policy",
    "PRICING": "pricing",
    "VEHICLE": "vehicle",
    "CITY": "city",
    "BOOKING": "faq",  
    "FAQ": "faq",
    "GENERAL": None,
}


_ENTITY_CATEGORY = {
    "REFUND": "policy",
    "CANCELLATION": "policy",
    "LUGGAGE": "policy",
    "PET": "policy",
    "AIRPORT": "policy",
    "VEHICLE_TYPE": "vehicle",
    "CITY": "city",
    "BOOKING": "faq",
}


def select_categories(
    intent: str, entity_labels: list[str]
) -> list[tuple[str, float]]:
   
    weights: dict[str, float] = {}

    primary = _INTENT_TO_CATEGORY.get(intent)
    entity_categories = {
        _ENTITY_CATEGORY[label] for label in entity_labels if label in _ENTITY_CATEGORY
    }

    if primary is not None:
        secondary = entity_categories - {primary}
        weights[primary] = 0.7 if secondary else 1.0
        if secondary:
            share = 0.3 / len(secondary)
            for category in secondary:
                weights[category] = share
    elif entity_categories:
       
        share = 1.0 / len(entity_categories)
        weights = {c: share for c in entity_categories}

    return sorted(weights.items(), key=lambda pair: pair[1], reverse=True)


def select_category(intent: str, entity_labels: list[str]) -> str | None:
    
    categories = select_categories(intent, entity_labels)
    return categories[0][0] if categories else None
