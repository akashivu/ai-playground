FIELD_QUESTIONS = {
    "pickup_location": "What is your pickup location?",
    "destination": "Where would you like to travel?",
    "travel_date": "What is your travel date?",
    "vehicle_type": "Which vehicle would you prefer? (e.g. Sedan, Innova, Tempo Traveller)",
}


def get_next_question(missing_fields: list[str]) -> str:
    """Returns the natural language question for the first missing field."""
    if not missing_fields:
        return ""
    return FIELD_QUESTIONS.get(missing_fields[0], f"Please provide your {missing_fields[0]}.")