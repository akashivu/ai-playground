from __future__ import annotations

import asyncio
from typing import Any

from langchain_components.planners.base_planner import BasePlanner
from langchain_components.planners.context import PlannerContext
from langchain_components.planners.registry import register_planner
from langchain_components.planners.result import ExecutionPlan, PlanningResult, PlanStep

from langchain_components.chains.itinerary_extraction_chain import (
    itinerary_extraction_chain,
)
from services.itinerary_prompt_service import get_next_question
from services.itinerary_session_service import itinerary_session_service
from services.itinerary_validation_service import find_missing_fields

_ITINERARY_FIELDS = ("destination", "days", "budget", "travelers", "interests")


@register_planner
class ItineraryPlanner(BasePlanner):
    name = "itinerary_planner"
    description = (
        "Rule-based slot-filling planner for trip itineraries. Extracts "
        "fields from the user's message via itinerary_extraction_chain, "
        "merges into persisted state, and either asks for what's missing "
        "or produces a generate_itinerary plan once destination and days "
        "are known."
    )

    async def create_plan(
        self, request: dict[str, Any], context: PlannerContext
    ) -> PlanningResult:
        user_id = context.user_id or request.get("user_id")
        session_id = context.session_id or request.get("session_id")

        previous = (
            itinerary_session_service.get(user_id=user_id, session_id=session_id) or {}
        )

        message = request.get("message", "")
        extracted: dict[str, Any] = {}
        if message:
            extracted = await asyncio.to_thread(
                itinerary_extraction_chain.invoke, {"question": message}
            )

        structured = {
            field: request[field] for field in _ITINERARY_FIELDS if field in request
        }
        new_data = {**extracted, **structured}

        merged = itinerary_session_service.merge(previous, new_data)
        itinerary_session_service.save(
            user_id=user_id, session_id=session_id, itinerary=merged
        )

        missing = find_missing_fields(merged)
        if missing:
            return PlanningResult.need_more_information(
                response=get_next_question(missing),
                missing_fields=missing,
                metadata={"itinerary_details": merged},
            )

        step = PlanStep(
            tool_name="generate_itinerary",
            input={field: merged.get(field) for field in _ITINERARY_FIELDS},
            description="Generate the trip itinerary",
        )
        plan = ExecutionPlan(
            goal="generate itinerary",
            steps=[step],
            metadata={"itinerary_details": merged, "completed": True},
        )
        return PlanningResult.ready(plan=plan, metadata={"itinerary_details": merged})