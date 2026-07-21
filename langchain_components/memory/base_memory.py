from __future__ import annotations

import abc
from typing import Any, ClassVar

from langchain_components.memory.context import MemoryContext
from langchain_components.memory.result import MemoryEntry, MemoryResult


class BaseMemory(abc.ABC):
    name: ClassVar[str]
    description: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC in cls.__bases__:
            return
        for attr in ("name", "description"):
            if getattr(cls, attr, None) is None:
                raise TypeError(f"{cls.__name__} must define class attribute '{attr}'")

    @abc.abstractmethod
    async def load(self, context: MemoryContext) -> MemoryResult:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, context: MemoryContext, entries: list[MemoryEntry]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def search(
        self, context: MemoryContext, query: str, top_k: int = 5
    ) -> MemoryResult:
        raise NotImplementedError

    @abc.abstractmethod
    async def clear(self, context: MemoryContext) -> None:
        raise NotImplementedError