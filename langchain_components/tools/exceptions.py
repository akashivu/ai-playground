from __future__ import annotations


class ToolError(Exception):
    """Base class for all tool-related errors."""


class ToolNotFoundError(ToolError):
    def __init__(self, name: str):
        super().__init__(f"Tool '{name}' is not registered.")
        self.name = name


class ToolAlreadyRegisteredError(ToolError):
    def __init__(self, name: str):
        super().__init__(f"Tool '{name}' is already registered.")
        self.name = name


class ToolValidationError(ToolError):
    def __init__(self, name: str, detail: str):
        super().__init__(f"Invalid input for tool '{name}': {detail}")
        self.name = name
        self.detail = detail


class ToolPermissionError(ToolError):
    def __init__(self, name: str, required: str):
        super().__init__(
            f"Caller lacks permission '{required}' required by tool '{name}'."
        )
        self.name = name
        self.required = required


class ToolTimeoutError(ToolError):
    def __init__(self, name: str, timeout_seconds: float):
        super().__init__(f"Tool '{name}' timed out after {timeout_seconds}s.")
        self.name = name
        self.timeout_seconds = timeout_seconds


class ToolExecutionError(ToolError):
    """Raised (or translated from) a tool's own execute() failing."""

    def __init__(self, name: str, detail: str, *, cause: Exception | None = None):
        super().__init__(f"Tool '{name}' failed: {detail}")
        self.name = name
        self.detail = detail
        if cause is not None:
            self.__cause__ = cause