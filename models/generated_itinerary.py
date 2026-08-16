from __future__ import annotations

from pydantic import BaseModel, Field


class ItineraryPlace(BaseModel):
    name: str
    period: str | None = None


class ItineraryDay(BaseModel):
    day: int
    title: str
    places: list[ItineraryPlace] = Field(default_factory=list)


class GeneratedItinerary(BaseModel):
    title: str
    answer_markdown: str
    days: list[ItineraryDay] = Field(default_factory=list)