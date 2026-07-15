PROMPTS = {
    "destination":
        "Where would you like to travel?",

    "days":
        "How many days is your trip?",

    "budget":
        "What's your approximate budget?",

    "travelers":
        "How many people are travelling?",

    "interests":
        (
            "What are your interests?\n\n"
            "Examples:\n"
            "• Beaches\n"
            "• Adventure\n"
            "• Food\n"
            "• Temples\n"
            "• Nature\n"
            "• Nightlife"
        ),
}


def get_next_question(missing: list[str],) -> str:
    if not missing:
        return "I have everything needed."

    return PROMPTS.get(missing[0],"Please provide more details.",)