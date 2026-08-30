from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from models.destination import Destination

logger = logging.getLogger(__name__)

_DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "destinations.json"


class DestinationRepository(Protocol):
    """Contract for anything that can supply destination records.

    Swap the JSON-backed implementation for a DB-backed one later
    without touching DestinationService or anything above it.
    """

    def get_by_id(self, destination_id: str) -> Destination | None: ...
    def get_by_name(self, name: str) -> Destination | None: ...
    def get_all(self) -> list[Destination]: ...


class JsonDestinationRepository:
    """Curated catalog loaded from a JSON fixture.

    A placeholder until destinations move into Postgres or an
    external data provider — the interface above is what makes
    that swap cheap. Fails fast on load if the fixture is malformed
    or contains duplicate ids/names, rather than silently serving
    a corrupted catalog.
    """

    def __init__(self, data_path: Path = _DEFAULT_DATA_PATH) -> None:
        self._by_id: dict[str, Destination] = {}
        self._by_name: dict[str, Destination] = {}
        self._load(data_path)

    def _load(self, data_path: Path) -> None:
        raw = json.loads(data_path.read_text(encoding="utf-8"))

        for entry in raw:
            destination = Destination.model_validate(entry)

            if destination.id in self._by_id:
                raise ValueError(f"duplicate destination id in {data_path.name}: {destination.id!r}")

            normalized_name = destination.name.strip().lower()
            if normalized_name in self._by_name:
                raise ValueError(f"duplicate destination name in {data_path.name}: {destination.name!r}")

            self._by_id[destination.id] = destination
            self._by_name[normalized_name] = destination

        logger.info("loaded %d destinations from %s", len(self._by_id), data_path)

    def get_by_id(self, destination_id: str) -> Destination | None:
        return self._by_id.get(destination_id)

    def get_by_name(self, name: str) -> Destination | None:
        return self._by_name.get(name.strip().lower())

    def get_all(self) -> list[Destination]:
        return list(self._by_id.values())


class DestinationService:
    """Application-facing entry point for destination lookups."""

    def __init__(self, repository: DestinationRepository) -> None:
        self._repository = repository

    def get_by_id(self, destination_id: str) -> Destination | None:
        return self._repository.get_by_id(destination_id)

    def get_by_name(self, name: str) -> Destination | None:
        destination = self._repository.get_by_name(name)
        if destination is None:
            logger.debug("destination not found for name=%r", name)
        return destination

    def get_all(self) -> list[Destination]:
        return self._repository.get_all()


@lru_cache
def get_destination_service() -> DestinationService:
    """FastAPI dependency — one shared instance per process."""
    return DestinationService(repository=JsonDestinationRepository())