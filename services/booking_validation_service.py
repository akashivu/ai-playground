REQUIRED_FIELDS = ["pickup_location", "destination", "travel_date"]

FIELD_LABELS = {
    "pickup_location": "Pickup Location",
    "destination": "Destination",
    "travel_date": "Travel Date",
}


def find_missing_fields(booking: dict) -> list[str]:
    """Returns list of required fields that are missing or empty."""
    return [
        field for field in REQUIRED_FIELDS
        if not booking.get(field)
    ]


def format_missing_fields(missing: list[str]) -> str:
    """Returns human-readable labels for missing fields."""
    return ", ".join(FIELD_LABELS.get(f, f) for f in missing)