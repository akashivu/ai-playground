BOOKING_PROMPTS = {
    "name": (
        "May I have your full name for the booking?"
    ),

    "email": (
        "Which email address should we send your booking confirmation to?"
    ),

    "mobile": (
        "Please share your mobile number."
    ),

    "trip_category": (
        "Which booking category would you like?\n\n"
        "• Outstation\n"
        "• Airport Transfer\n"
        "• Rental"
    ),
  

    "trip_type": (
        "Would you like:\n\n"
        "• One Way\n"
        "• Round Trip"
    ),

    "pickup_location": (
        "Where should we pick you up?"
    ),

    "destination": (
        "Where would you like to travel?"
    ),

    "city": (
        "Which city is this trip in?"
    ),

    "pickup_address": (
        "Please share the exact pickup address."
    ),

    "travel_date": (
        "On which date would you like to travel? "
        "(Example: 25 July 2026)"
    ),

    "pickup_time": (
        "What time should the driver arrive?"
    ),

    "vehicle_type": (
        "Which vehicle would you prefer?\n\n"
        "• Sedan\n"
        "• SUV\n"
        "• Innova\n"
        "• Tempo Traveller"
    ),
}


def get_next_question(
    missing_fields: list[str],
) -> str:
    """
    Returns the next conversational prompt for the
    first missing booking field.
    """

    if not missing_fields:
        return (
            "Thank you. I have everything needed "
            "to process your booking."
        )

    return BOOKING_PROMPTS.get(
        missing_fields[0],
        "Could you please provide the remaining booking information?",
    )
