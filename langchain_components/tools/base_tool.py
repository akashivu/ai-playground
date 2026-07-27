from __future__ import annotations

import abc
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

from langchain_components.tools.schemas import ToolCallContext, ToolResult

RequestT = TypeVar("RequestT", bound=BaseModel)


class BaseTool(abc.ABC, Generic[RequestT]):
    
    name: ClassVar[str]
    description: ClassVar[str]
    schema: ClassVar[type[BaseModel]]

    # Optional per-tool policy — safe defaults, override as needed.
    requires_permission: ClassVar[str | None] = None
    timeout_seconds: ClassVar[float] = 15.0
    max_retries: ClassVar[int] = 0
    idempotent: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC in cls.__bases__:
            return  # allow intermediate abstract subclasses
        for attr in ("name", "description", "schema"):
            if getattr(cls, attr, None) is None:
                raise TypeError(f"{cls.__name__} must define class attribute '{attr}'")

    @abc.abstractmethod
    async def execute(self, request: RequestT, context: ToolCallContext) -> ToolResult:
        
        raise NotImplementedError