from __future__ import annotations

import asyncio
from typing import Any

from langchain_components.planners.base_planner import BasePlanner
from langchain_components.planners.context import PlannerContext
from langchain_components.planners.registry import register_planner
from langchain_components.planners.result import ExecutionPlan, PlanningResult, PlanStep

from langchain_components.chains.booking_extraction_chain import (
    booking_extraction_chain,
)
from services.booking_prompt_service import get_next_question
from services.booking_session_service import booking_session_service
from services.booking_validation_service import find_missing_fields

_BOOKING_FIELDS = (
    "name",
    "email",
    "mobile",
    "trip_category",
    "trip_type",
    "pickup_location",
    "destination",
    "city",
    "pickup_address",
    "travel_date",
    "pickup_time",
    "vehicle_type",
)


@register_planner
class BookingPlanner(BasePlanner):
    name = "booking_planner"
    description = (
        "Slot-filling planner for cab bookings. Extracts fields from the "
        "user's free-text message via booking_extraction_chain, merges "
        "with any structured fields already on the request and with "
        "persisted booking state, and either asks for what's missing or "
        "produces a create_booking plan once complete."
    )

    async def create_plan(
        self, request: dict[str, Any], context: PlannerContext
    ) -> PlanningResult:
        user_id = context.user_id or request.get("user_id")
        session_id = context.session_id or request.get("session_id")

        previous_booking = (
            booking_session_service.get_booking(user_id=user_id, session_id=session_id)
            or {}
        )

        message = request.get("message", "")
        extracted_from_text: dict[str, Any] = {}
        if message:
            extracted_from_text = await asyncio.to_thread(
                booking_extraction_chain.invoke, {"question": message}
            )

        structured = {
            field: request[field] for field in _BOOKING_FIELDS if field in request
        }
        new_data = {**extracted_from_text, **structured}

        merged_booking = booking_session_service.merge_booking(
            previous_booking, new_data
        )
        booking_session_service.save_booking(
            user_id=user_id, session_id=session_id, booking=merged_booking
        )

        missing = find_missing_fields(merged_booking)
        if missing:
            return PlanningResult.need_more_information(
                response=get_next_question(missing),
                missing_fields=missing,
                metadata={"booking_details": merged_booking},
            )

        step = PlanStep(
            tool_name="create_booking",
            input={field: merged_booking.get(field) for field in _BOOKING_FIELDS},
            description="Create the confirmed booking",
        )
        plan = ExecutionPlan(
            goal="create booking",
            steps=[step],
            metadata={"booking_details": merged_booking, "completed": True},
        )
        return PlanningResult.ready(
            plan=plan, metadata={"booking_details": merged_booking}
        )