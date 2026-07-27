from __future__ import annotations

from pydantic import BaseModel

from langchain_components.tools.base_tool import BaseTool
from langchain_components.tools.permissions import Permission
from langchain_components.tools.registry import register_tool
from langchain_components.tools.schemas import ToolCallContext, ToolResult


class PingRequest(BaseModel):
    message: str


@register_tool
class PingTool(BaseTool):
    name = "ping"
    description = (
        "Trivial example tool for testing the framework - echoes its input back."
    )
    schema = PingRequest
    requires_permission = Permission.READ.value
    timeout_seconds = 5.0
    max_retries = 1
    idempotent = True

    async def execute(
        self, request: PingRequest, context: ToolCallContext
    ) -> ToolResult:
        return ToolResult.ok(data={"pong": True, "echo": request.message})