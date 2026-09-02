from __future__ import annotations

from pydantic import BaseModel, Field


class TravelerPreferenceUpdate(BaseModel):
    """LLM-extracted explicit preferences from a single message.

    Not persisted directly — merged into TravelerProfile by
    TravelerPreferenceService, which re-runs normalization.
    """

    interests: list[str] = Field(default_factory=list)
    travel_styles: list[str] = Field(default_factory=list)
    preferred_pace: str | None = None
    traveling_with: list[str] = Field(default_factory=list)
    budget_level: str | None = None
    favorite_destinations: list[str] = Field(default_factory=list)
    avoided_preferences: list[str] = Field(default_factory=list)