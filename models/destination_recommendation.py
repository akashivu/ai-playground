from __future__ import annotations

from pydantic import BaseModel, Field

from models.destination import Destination


class DestinationRecommendation(BaseModel):
    destination: Destination

    score: float = Field(ge=0)

    matched_interests: list[str] = Field(default_factory=list)
    matched_styles: list[str] = Field(default_factory=list)
    matched_companions: list[str] = Field(default_factory=list)
    matched_avoided: list[str] = Field(default_factory=list)

    duration_match: bool = False

    reasons: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}