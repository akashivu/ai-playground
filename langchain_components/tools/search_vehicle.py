from __future__ import annotations
from pydantic import BaseModel, Field
from langchain_components.tools.base_tool import BaseTool
from langchain_components.tools.exceptions import ToolExecutionError
from langchain_components.tools.permissions import Permission
from langchain_components.tools.registry import register_tool
from langchain_components.tools.schemas import ToolResult


class SearchVehicleRequest(BaseModel):
    pickup_location: str
    dropoff_location: str
    vehicle_type: str | None = Field(
        default=None, description="e.g. 'sedan', 'suv' — omit to search all"
    )


@register_tool
class SearchVehicleTool(BaseTool):
    name = "search_vehicle"
    description = "Search available vehicles for a given pickup/dropoff location, optionally filtered by vehicle type."
    schema = SearchVehicleRequest
    requires_permission = Permission.READ.value
    timeout_seconds = 8.0
    max_retries = 1
    idempotent = True

    async def execute(self, request: SearchVehicleRequest) -> ToolResult:
        try:
            vehicles = [
                {
                    "vehicle_id": "veh_101",
                    "type": "sedan",
                    "eta_minutes": 6,
                    "fare_estimate": 240,
                },
                {
                    "vehicle_id": "veh_204",
                    "type": "suv",
                    "eta_minutes": 9,
                    "fare_estimate": 380,
                },
            ]
            if request.vehicle_type:
                vehicles = [v for v in vehicles if v["type"] == request.vehicle_type]
            return ToolResult.ok(data={"vehicles": vehicles})
        except Exception as exc:
            raise ToolExecutionError(self.name, str(exc), cause=exc) from exc