from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from langchain_components.tools.exceptions import (
    ToolError,
    ToolExecutionError,
    ToolPermissionError,
    ToolTimeoutError,
    ToolValidationError,
)
from langchain_components.tools.hooks import ExecutorHooks
from langchain_components.tools.metrics import MetricsSink, NoOpMetricsSink
from langchain_components.tools.permissions import (
    AllowAllPermissionChecker,
    PermissionChecker,
    enforce,
)
from langchain_components.tools.registry import ToolRegistry, tool_registry
from langchain_components.tools.schemas import (
    ToolAuditRecord,
    ToolCallContext,
    ToolErrorType,
    ToolResult,
)

logger = logging.getLogger("tools.executor")

AuditSink = Callable[[ToolAuditRecord], None]


def _default_audit_sink(record: ToolAuditRecord) -> None:
    logger.info(
        "tool_call name=%s success=%s duration_ms=%.1f retries=%d "
        "trace_id=%s session_id=%s agent=%s",
        record.tool_name,
        record.success,
        record.duration_ms,
        record.retries,
        record.trace_id,
        record.session_id,
        record.agent_name,
    )


class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        permission_checker: PermissionChecker | None = None,
        audit_sink: AuditSink = _default_audit_sink,
        metrics: MetricsSink | None = None,
        hooks: ExecutorHooks | None = None,
    ) -> None:
        self._registry = registry or tool_registry
        self._permission_checker = permission_checker or AllowAllPermissionChecker()
        self._audit_sink = audit_sink
        self._metrics = metrics or NoOpMetricsSink()
        self._hooks = hooks or ExecutorHooks()

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    async def run(
        self,
        tool_name: str,
        raw_input: dict[str, Any],
        context: ToolCallContext | None = None,
    ) -> ToolResult:
        context = context or ToolCallContext()
        tool = self._registry.get(tool_name)  # raises ToolNotFoundError — a real bug,
        # not a bad request, so this is the one case allowed to propagate.

        self._hooks.fire_before(tool.name, context, raw_input)

        start = time.perf_counter()

        try:
            enforce(
                self._permission_checker, context, tool.name, tool.requires_permission
            )
            validated = self._validate(tool.name, tool.schema, raw_input)
        except (ToolPermissionError, ToolValidationError) as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            error_type = (
                ToolErrorType.PERMISSION
                if isinstance(exc, ToolPermissionError)
                else ToolErrorType.VALIDATION
            )
            error_result = ToolResult.fail(
                error=str(exc),
                error_type=error_type,
                tool_name=tool.name,
                duration_ms=duration_ms,
                retries=0,
            )
            self._audit_invalid(
                context, tool.name, raw_input, error_result, duration_ms
            )
            self._hooks.fire_error(tool.name, context, exc)
            self._metrics.record_duration(tool.name, duration_ms)
            self._metrics.increment_failure(tool.name)
            self._hooks.fire_after(tool.name, context, error_result)
            return error_result

        retries_used = 0
        last_error: Exception | None = None
        last_error_type: ToolErrorType | None = None
        attempts_allowed = max(1, tool.max_retries + 1)

        for attempt in range(attempts_allowed):
            retries_used = attempt
            try:
                result = await asyncio.wait_for(
                    tool.execute(validated, context), timeout=tool.timeout_seconds
                )
                duration_ms = (time.perf_counter() - start) * 1000
                result.tool_name = tool.name
                result.duration_ms = duration_ms
                result.retries = retries_used
                self._audit(
                    context, tool.name, validated, result, duration_ms, retries_used
                )
                self._metrics.record_duration(tool.name, duration_ms)
                self._metrics.increment_success(tool.name)
                self._hooks.fire_after(tool.name, context, result)
                return result

            except asyncio.TimeoutError:
                last_error = ToolTimeoutError(tool.name, tool.timeout_seconds)
                last_error_type = ToolErrorType.TIMEOUT
                self._hooks.fire_error(tool.name, context, last_error)
            except ToolError as exc:
                last_error = exc
                last_error_type = ToolErrorType.EXECUTION
                self._hooks.fire_error(tool.name, context, exc)
                if not tool.idempotent:
                    break  # don't blindly retry non-idempotent failures
            except Exception as exc:  # noqa: BLE001 — translate every unknown error
                last_error = ToolExecutionError(tool.name, str(exc), cause=exc)
                last_error_type = ToolErrorType.EXECUTION
                self._hooks.fire_error(tool.name, context, last_error)
                if not tool.idempotent:
                    break

            if attempt < attempts_allowed - 1:
                await asyncio.sleep(min(2**attempt, 8))  # simple exponential backoff

        duration_ms = (time.perf_counter() - start) * 1000
        error_result = ToolResult.fail(
            error=str(last_error) if last_error else "Unknown tool failure",
            error_type=last_error_type,
            tool_name=tool.name,
            duration_ms=duration_ms,
            retries=retries_used,
        )
        self._audit(
            context, tool.name, validated, error_result, duration_ms, retries_used
        )
        self._metrics.record_duration(tool.name, duration_ms)
        if isinstance(last_error, ToolTimeoutError):
            self._metrics.increment_timeout(tool.name)
        else:
            self._metrics.increment_failure(tool.name)
        self._hooks.fire_after(tool.name, context, error_result)
        return error_result

    @staticmethod
    def _validate(
        tool_name: str, schema: type[BaseModel], raw_input: dict[str, Any]
    ) -> BaseModel:
        try:
            return schema.model_validate(raw_input)
        except ValidationError as exc:
            raise ToolValidationError(tool_name, str(exc)) from exc

    def _audit(
        self,
        context: ToolCallContext,
        tool_name: str,
        validated_input: BaseModel,
        result: ToolResult,
        duration_ms: float,
        retries: int,
    ) -> None:
        self._emit_audit(
            context,
            tool_name,
            validated_input.model_dump(),
            result,
            duration_ms,
            retries,
        )

    def _audit_invalid(
        self,
        context: ToolCallContext,
        tool_name: str,
        raw_input: dict[str, Any],
        result: ToolResult,
        duration_ms: float,
    ) -> None:

        self._emit_audit(context, tool_name, raw_input, result, duration_ms, 0)

    def _emit_audit(
        self,
        context: ToolCallContext,
        tool_name: str,
        request_payload: dict[str, Any],
        result: ToolResult,
        duration_ms: float,
        retries: int,
    ) -> None:
        record = ToolAuditRecord(
            trace_id=context.trace_id,
            tool_name=tool_name,
            execution_id=result.execution_id,
            session_id=context.session_id,
            user_id=context.user_id,
            agent_name=context.agent_name,
            request_payload=request_payload,
            success=result.success,
            error=result.error,
            duration_ms=duration_ms,
            retries=retries,
        )
        self._audit_sink(record)


tool_executor = ToolExecutor()