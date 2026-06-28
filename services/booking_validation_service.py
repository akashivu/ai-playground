REQUIRED_FIELDS = [
    "name",
    "email",
    "mobile",
    "trip_category",
    "trip_type",
    "pickup_location",
    "destination",
    "travel_date",
    "pickup_time",
    "vehicle_type",
]

FIELD_LABELS = {
    "name": "Customer Name",
    "email": "Email Address",
    "mobile": "Mobile Number",
    "trip_category": "Trip Category",
    "trip_type": "Trip Type",
    "pickup_location": "Pickup Location",
    "destination": "Destination",
    "travel_date": "Travel Date",
    "pickup_time": "Pickup Time",
    "vehicle_type": "Vehicle Type",
}


def find_missing_fields(booking: dict) -> list[str]:
    """
    Returns all required booking fields that
    are missing or empty.
    """

    missing = []

    for field in REQUIRED_FIELDS:
        value = booking.get(field)

        if value is None:
            missing.append(field)
            continue

        if isinstance(value, str) and not value.strip():
            missing.append(field)

    return missing


def format_missing_fields(missing: list[str]) -> str:
    """
    Human readable field names.
    """

    return ", ".join(
        FIELD_LABELS.get(field, field)
        for field in missing
    )