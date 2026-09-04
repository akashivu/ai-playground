from __future__ import annotations

from models.destination_recommendation import DestinationRecommendation
from models.traveler_profile import TravelerProfile


def format_profile_for_prompt(profile: TravelerProfile) -> str:
    """Renders a traveler profile as plain text for LLM context.

    Deliberately excludes nothing sensitive here — profile fields are
    already just travel preferences — but keeps the shape simple and
    readable rather than dumping raw JSON/repr at the model.
    """
    lines = []
    if profile.interests:
        lines.append(f"Interests: {', '.join(profile.interests)}")
    if profile.travel_styles:
        lines.append(f"Travel styles: {', '.join(profile.travel_styles)}")
    if profile.traveling_with:
        lines.append(f"Traveling with: {', '.join(profile.traveling_with)}")
    if profile.preferred_pace:
        lines.append(f"Preferred pace: {profile.preferred_pace}")
    if profile.budget_level:
        lines.append(f"Budget level: {profile.budget_level}")
    if profile.avoided_preferences:
        lines.append(f"Prefers to avoid: {', '.join(profile.avoided_preferences)}")

    return "\n".join(lines) if lines else "No stated preferences yet."


def format_recommendations_for_prompt(recommendations: list[DestinationRecommendation]) -> str:
   
    if not recommendations:
        return "No matching destinations found."

    blocks = []
    for i, rec in enumerate(recommendations, start=1):
        destination = rec.destination
        location = f"{destination.name}, {destination.state}" if destination.state else destination.name

        block = [f"{i}. {location}"]
        if destination.description:
            block.append(f"   Description: {destination.description}")
        if rec.reasons:
            block.append(f"   Why it fits: {'; '.join(rec.reasons)}")

        blocks.append("\n".join(block))

    return "\n\n".join(blocks)