from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from langchain_components.tools.schemas import ToolCallContext, ToolResult

logger = logging.getLogger("tools.hooks")

BeforeExecuteHook = Callable[[str, ToolCallContext, dict[str, Any]], None]
AfterExecuteHook = Callable[[str, ToolCallContext, ToolResult], None]
OnErrorHook = Callable[[str, ToolCallContext, Exception], None]


@dataclass
class ExecutorHooks:
    

    before_execute: BeforeExecuteHook | None = None
    after_execute: AfterExecuteHook | None = None
    on_error: OnErrorHook | None = None

    def fire_before(
        self, tool_name: str, context: ToolCallContext, raw_input: dict[str, Any]
    ) -> None:
        self._safe_call(self.before_execute, tool_name, context, raw_input)

    def fire_after(self, tool_name: str, context: ToolCallContext, result: ToolResult) -> None:
        self._safe_call(self.after_execute, tool_name, context, result)

    def fire_error(self, tool_name: str, context: ToolCallContext, error: Exception) -> None:
        self._safe_call(self.on_error, tool_name, context, error)

    @staticmethod
    def _safe_call(hook: Callable[..., None] | None, *args: Any) -> None:
        if hook is None:
            return
        try:
            hook(*args)
        except Exception:  
            logger.exception("Executor hook raised; ignoring and continuing.")