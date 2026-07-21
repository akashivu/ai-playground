from __future__ import annotations

from typing import Iterable

from langchain_components.memory.base_memory import BaseMemory
from langchain_components.memory.exceptions import (
    MemoryAlreadyRegisteredError,
    MemoryNotFoundError,
)


class MemoryRegistry:
    _instance: "MemoryRegistry | None" = None

    def __init__(self) -> None:
        self._backends: dict[str, BaseMemory] = {}

    @classmethod
    def instance(cls) -> "MemoryRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, memory: BaseMemory, *, overwrite: bool = False) -> None:
        if not overwrite and memory.name in self._backends:
            raise MemoryAlreadyRegisteredError(memory.name)
        self._backends[memory.name] = memory

    def get(self, name: str) -> BaseMemory:
        try:
            return self._backends[name]
        except KeyError as exc:
            raise MemoryNotFoundError(name) from exc

    def has(self, name: str) -> bool:
        return name in self._backends

    def list_memories(self) -> Iterable[BaseMemory]:
        return list(self._backends.values())

    def list_names(self) -> list[str]:
        return sorted(self._backends.keys())

    def describe_all(self) -> list[dict[str, str]]:
        return [
            {"name": m.name, "description": m.description} for m in self.list_memories()
        ]

    def clear(self) -> None:
        self._backends.clear()


memory_registry = MemoryRegistry.instance()


def register_memory(cls: type[BaseMemory]) -> type[BaseMemory]:
    instance = cls()
    memory_registry.register(instance)
    return cls