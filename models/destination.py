from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Destination(BaseModel):
    """Canonical internal representation of a travel destination.

    This is application data — never something the LLM invents or edits.
    """

    id: str
    name: str
    country: str = "India"
    state: str | None = None

    description: str | None = None

    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    best_for: list[str] = Field(default_factory=list)
    travel_styles: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)

    ideal_duration_days: int | None = Field(default=None, gt=0)

    model_config = {"frozen": True}

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be blank")
        return v

    @field_validator("country")
    @classmethod
    def _india_only(cls, v: str) -> str:
        if v != "India":
            raise ValueError(f"unsupported country for Stage 2: {v!r} (India-only scope)")
        return v

    @field_validator("best_for", "travel_styles", "interests")
    @classmethod
    def _normalize_tags(cls, v: list[str]) -> list[str]:
        return [tag.strip().lower() for tag in v if tag.strip()]