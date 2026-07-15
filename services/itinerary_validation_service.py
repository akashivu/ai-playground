REQUIRED_FIELDS = ["destination","days",]


def find_missing_fields(itinerary: dict,) -> list[str]:
    missing = []

    for field in REQUIRED_FIELDS:
        value = itinerary.get(field)

        if value is None:
            missing.append(field)
            continue

        if isinstance(value, str) and not value.strip():
            missing.append(field)

    return missing