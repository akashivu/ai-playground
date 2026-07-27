from __future__ import annotations

import asyncio

from pydantic import BaseModel

from langchain_components.tools.base_tool import BaseTool
from langchain_components.tools.exceptions import ToolExecutionError
from langchain_components.tools.permissions import Permission
from langchain_components.tools.registry import register_tool
from langchain_components.tools.schemas import ToolCallContext, ToolResult

from models.booking_result import BookingResult
from services.booking_orchestrator import booking_orchestrator


class GetBookingStatusRequest(BaseModel):
    booking_id: int


@register_tool
class GetBookingStatusTool(BaseTool):
    name = "get_booking_status"
    description = "Look up the current status of an existing booking by its ID."
    schema = GetBookingStatusRequest
    requires_permission = Permission.READ.value
    timeout_seconds = 10.0
    max_retries = 1
    idempotent = True

    async def execute(
        self, request: GetBookingStatusRequest, context: ToolCallContext
    ) -> ToolResult:
        current_user = context.metadata.get("current_user")

        try:
            result: BookingResult = await asyncio.to_thread(
                booking_orchestrator.get_booking_status,
                booking_id=request.booking_id,
                current_user=current_user,
            )
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(self.name, str(exc), cause=exc) from exc

        if not result.success:
            return ToolResult.fail(error=result.message, data=result.model_dump())

        return ToolResult.ok(data=result.model_dump())