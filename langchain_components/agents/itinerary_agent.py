from __future__ import annotations

from langchain_components.agents.base_agent import BaseAgent
from langchain_components.agents.registry import register_agent
from langchain_components.execution.executor import PlanExecutor
from langchain_components.planners.base_planner import BasePlanner
from langchain_components.planners.registry import planner_registry
from langchain_components.tools.executor import ToolExecutor

import langchain_components.planners.itinerary_planner  
import langchain_components.tools.itinerary.generate_itinerary_tool  


@register_agent
class ItineraryAgent(BaseAgent):
    name = "itinerary_agent"
    description = (
        "Handles trip itinerary requests: collects trip details turn by "
        "turn, then generates a full itinerary once complete."
    )

    def __init__(
        self,
        tool_executor: ToolExecutor | None = None,
        planner: BasePlanner | None = None,
        plan_executor: PlanExecutor | None = None,
    ) -> None:
        super().__init__(
            tool_executor=tool_executor,
            planner=planner or planner_registry.get("itinerary_planner"),
            plan_executor=plan_executor,
        )