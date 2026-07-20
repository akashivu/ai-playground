from __future__ import annotations

import enum
from typing import Protocol

from langchain_components.tools.exceptions import ToolPermissionError
from langchain_components.tools.schemas import ToolCallContext


class Permission(str, enum.Enum):
   

    READ = "read"
    BOOKING_WRITE = "booking:write"
    BOOKING_CANCEL = "booking:cancel"
    PAYMENT_WRITE = "payment:write"
    EMAIL_SEND = "email:send"
    ADMIN = "admin"


class PermissionChecker(Protocol):
    """Pluggable authorization strategy, injected into the ToolExecutor."""

    def is_allowed(self, context: ToolCallContext, required: str) -> bool: ...


class AllowAllPermissionChecker:
    """Default checker for local/dev — every call is allowed.

    Swap for a real implementation (RBAC lookup, session scopes, role
    claims, etc.) when wiring the executor for production traffic.
    """

    def is_allowed(self, context: ToolCallContext, required: str) -> bool:
        return True


class DenyIfMissingUserChecker:
    

    def is_allowed(self, context: ToolCallContext, required: str) -> bool:
        if required == Permission.READ.value:
            return True
        return context.user_id is not None


def enforce(
    checker: PermissionChecker,
    context: ToolCallContext,
    tool_name: str,
    required: str | None,
) -> None:
    if required is None:
        return
    if not checker.is_allowed(context, required):
        raise ToolPermissionError(tool_name, required)