from __future__ import annotations

from langchain_components.agents.base_agent import BaseAgent
from langchain_components.agents.registry import register_agent
from langchain_components.execution.executor import PlanExecutor
from langchain_components.planners.base_planner import BasePlanner
from langchain_components.planners.registry import planner_registry
from langchain_components.tools.executor import ToolExecutor

import langchain_components.planners.booking_planner  # noqa: F401
import langchain_components.tools.booking.create_booking_tool  # noqa: F401
import langchain_components.tools.booking.get_booking_status_tool  # noqa: F401


@register_agent
class BookingAgent(BaseAgent):
    name = "booking_agent"
    description = (
        "Handles cab booking requests: collects required trip details "
        "turn by turn, then creates the booking once complete."
    )

    def __init__(
        self,
        tool_executor: ToolExecutor | None = None,
        planner: BasePlanner | None = None,
        plan_executor: PlanExecutor | None = None,
    ) -> None:
        super().__init__(
            tool_executor=tool_executor,
            planner=planner or planner_registry.get("booking_planner"),
            plan_executor=plan_executor,
        )