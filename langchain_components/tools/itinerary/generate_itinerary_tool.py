from __future__ import annotations

import asyncio

from pydantic import BaseModel, ValidationError

from langchain_components.tools.base_tool import BaseTool
from langchain_components.tools.exceptions import ToolExecutionError
from langchain_components.tools.permissions import Permission
from langchain_components.tools.registry import register_tool
from langchain_components.tools.schemas import ToolCallContext, ToolResult

from models.itinerary_details import ItineraryDetails
from langchain_components.chains.itinerary_generation_chain import (
    itinerary_generation_chain,
)


class GenerateItineraryRequest(BaseModel):
    destination: str
    days: int
    budget: int | None = None
    travelers: int | None = None
    interests: str | None = None


@register_tool
class GenerateItineraryTool(BaseTool):
    name = "generate_itinerary"
    description = (
        "Generate a full day-wise trip itinerary once destination and trip "
        "length are known. Delegates to the existing itinerary_generation_chain."
    )
    schema = GenerateItineraryRequest
    requires_permission = Permission.READ.value
    timeout_seconds = 30.0
    max_retries = 1
    idempotent = True

    async def execute(
        self, request: GenerateItineraryRequest, context: ToolCallContext
    ) -> ToolResult:
        try:
            details = ItineraryDetails(**request.model_dump())
        except ValidationError as exc:
            raise ToolExecutionError(
                self.name, f"invalid itinerary details: {exc}", cause=exc
            ) from exc

        try:
            response = await asyncio.to_thread(
                itinerary_generation_chain.invoke, details.model_dump()
            )
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(self.name, str(exc), cause=exc) from exc

        return ToolResult.ok(
            data={
                "destination": details.destination,
                "days": details.days,
                "itinerary": response.content,
            }
        )