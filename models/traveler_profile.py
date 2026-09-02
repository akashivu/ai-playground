from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class TravelerProfile(BaseModel):
    """Persistent traveler preferences used for personalization.

    Contains preferences only, not sensitive personal information.
    """

    interests: list[str] = Field(default_factory=list)
    travel_styles: list[str] = Field(default_factory=list)
    preferred_pace: str | None = None
    traveling_with: list[str] = Field(default_factory=list)
    budget_level: str | None = None
    favorite_destinations: list[str] = Field(default_factory=list)
    avoided_preferences: list[str] = Field(default_factory=list)

    @field_validator(
        "interests",
        "travel_styles",
        "traveling_with",
        "favorite_destinations",
        "avoided_preferences",
    )
    @classmethod
    def normalize_lists(cls, values: list[str]) -> list[str]:
        result: list[str] = []
        for value in values:
            normalized = value.strip().lower()
            if normalized and normalized not in result:
                result.append(normalized)
        return result

    @field_validator("preferred_pace", "budget_level")
    @classmethod
    def normalize_optional_string(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        return normalized or None