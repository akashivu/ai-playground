from __future__ import annotations

import asyncio

from pydantic import BaseModel, EmailStr, ValidationError

from langchain_components.tools.base_tool import BaseTool
from langchain_components.tools.exceptions import ToolExecutionError
from langchain_components.tools.permissions import Permission
from langchain_components.tools.registry import register_tool
from langchain_components.tools.schemas import ToolCallContext, ToolResult

from models.booking_confirmation import BookingConfirmation
from models.booking_result import BookingResult
from services.booking_orchestrator import booking_orchestrator


class CreateBookingRequest(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    trip_category: str
    trip_type: str
    pickup_location: str
    destination: str
    city: str | None = None
    pickup_address: str | None = None
    travel_date: str
    pickup_time: str
    vehicle_type: str


@register_tool
class CreateBookingTool(BaseTool):
    name = "create_booking"
    description = (
        "Create a confirmed cab booking once all required customer and "
        "trip details are known. Fare and distance are computed by the "
        "booking service, not supplied by the caller."
    )
    schema = CreateBookingRequest
    requires_permission = Permission.BOOKING_WRITE.value
    timeout_seconds = 15.0
    max_retries = 0
    idempotent = False

    async def execute(
        self, request: CreateBookingRequest, context: ToolCallContext
    ) -> ToolResult:
        try:
            confirmation = BookingConfirmation(**request.model_dump())
        except ValidationError as exc:
            raise ToolExecutionError(
                self.name, f"invalid booking confirmation: {exc}", cause=exc
            ) from exc

        current_user = context.metadata.get("current_user")

        try:
            result: BookingResult = await asyncio.to_thread(
                booking_orchestrator.create_booking,
                confirmation=confirmation,
                current_user=current_user,
            )
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(self.name, str(exc), cause=exc) from exc

        if not result.success:
            return ToolResult.fail(error=result.message, data=result.model_dump())

        return ToolResult.ok(
            data={**result.model_dump(), "confirmation": confirmation.model_dump()}
        )