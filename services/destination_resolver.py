from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

from models.destination import Destination
from services.destination_service import (
    DestinationService,
    get_destination_service,
)


@dataclass(frozen=True)
class DestinationResolution:
    destination: Destination | None
    confidence: float
    matched_by: str | None = None


class DestinationResolver:
    """
    Resolves user-provided destination text to a canonical
    Destination record.

    The resolver is deterministic. The LLM should not be used
    as the source of truth for destination identity.
    """

    def __init__(self, destination_service: DestinationService) -> None:
        self._destination_service = destination_service

    @staticmethod
    def _normalize(value: str) -> str:
        """Unicode/case/whitespace normalization only. Punctuation
        (notably commas) is deliberately preserved here so location
        suffixes can still be split out downstream."""
        value = unicodedata.normalize("NFKC", value)
        value = value.strip().lower()
        return re.sub(r"\s+", " ", value)

    @staticmethod
    def _strip_punctuation(value: str) -> str:
        value = re.sub(r"[^\w\s-]", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _remove_location_suffixes(value: str) -> str:
        """Removes trailing geographic qualifiers such as ', Karnataka'
        or ', India'. Must be called on text that still has its commas —
        i.e. before _strip_punctuation, not after."""
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if len(parts) <= 1:
            return value
        return parts[0]

    def resolve(self, text: str) -> DestinationResolution:
        normalized = self._normalize(text)

        if not normalized:
            return DestinationResolution(destination=None, confidence=0.0)

        # Exact canonical name
        clean = self._strip_punctuation(normalized)

        destination = self._destination_service.get_by_name(clean)
        if destination:
            return DestinationResolution(
                destination=destination,
                confidence=1.0,
                matched_by="exact_name",
            )

        # Name + state/country, e.g. "Coorg, Karnataka"
        base_name = self._remove_location_suffixes(normalized)
        base_name_clean = self._strip_punctuation(base_name)

        if base_name_clean != clean:
            destination = self._destination_service.get_by_name(base_name_clean)
            if destination:
                return DestinationResolution(
                    destination=destination,
                    confidence=0.98,
                    matched_by="name_with_location",
                )

        # Canonical ID
        destination = self._destination_service.get_by_id(clean)
        if destination:
            return DestinationResolution(
                destination=destination,
                confidence=1.0,
                matched_by="id",
            )

        return DestinationResolution(destination=None, confidence=0.0)


@lru_cache
def get_destination_resolver() -> DestinationResolver:
    return DestinationResolver(destination_service=get_destination_service())