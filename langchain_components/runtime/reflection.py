from __future__ import annotations

import logging
from typing import Protocol

from langchain_components.runtime.context import RuntimeContext
from langchain_components.runtime.models import ExecutionResult
from langchain_components.runtime.reflection_models import (
    ReflectionAction,
    ReflectionDecision,
    ReflectionPromptContext,
)
from langchain_components.tools.schemas import ToolErrorType, ToolResult

logger = logging.getLogger(__name__)

REFLECTION_SYSTEM_PROMPT = """You are the reflection layer of an AI agent runtime.
A tool step failed in a way the deterministic rules couldn't classify.
Decide what should happen next: RETRY, ASK_USER, or ABORT.
Only reference a tool or step name if it appears in the available tools or
remaining steps you were given — never invent one.
"""


class LLMReflector(Protocol):
    
    async def decide(self, prompt_context: ReflectionPromptContext) -> ReflectionDecision: ...


class NullLLMReflector:
    

    async def decide(self, prompt_context: ReflectionPromptContext) -> ReflectionDecision:
        return ReflectionDecision(
            action=ReflectionAction.ABORT,
            reason="No deterministic rule matched this failure and no LLM "
                   "reflector is configured, so aborting rather than guessing.",
            source="fallback",
        )


class LangChainLLMReflector:
    

    def __init__(self, model):
        self._structured_model = model.with_structured_output(ReflectionDecision)

    async def decide(self, prompt_context: ReflectionPromptContext) -> ReflectionDecision:
        prompt = self._build_prompt(prompt_context)
        try:
            decision = await self._structured_model.ainvoke(prompt)
        except Exception as exc:
            logger.error("LLM reflection call failed or returned invalid output: %s", exc)
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=f"LLM reflection failed: {exc}",
                source="fallback",
            )

        if not isinstance(decision, ReflectionDecision):
            logger.error("LLM reflection returned unexpected type: %r", type(decision))
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason="LLM reflection did not return a ReflectionDecision",
                source="fallback",
            )
        decision.source = "llm"
        return decision

    @staticmethod
    def _build_prompt(prompt_context: ReflectionPromptContext) -> str:
        return (
            f"{REFLECTION_SYSTEM_PROMPT}\n\n"
            f"Query: {prompt_context.query!r}\n"
            f"Failed step: {prompt_context.failed_step}\n"
            f"Error: {prompt_context.error}\n"
            f"Remaining steps: {prompt_context.remaining_step_names}\n"
            f"Available tools: {prompt_context.available_tool_names}"
        )


class ReflectionEngine:
    def __init__(self, llm_reflector: LLMReflector | None = None):
        self._llm_reflector = llm_reflector or NullLLMReflector()

    async def reflect(self, context: RuntimeContext, result: ExecutionResult) -> ReflectionDecision:
        decision = self._deterministic_check(context, result)

        if decision is None:
            decision = await self._llm_check(context, result)

        return self._validate(context, decision)

    def _deterministic_check(
        self, context: RuntimeContext, result: ExecutionResult
    ) -> ReflectionDecision | None:
        if result.success:
            remaining = [s for s in context.state.plan if not s.completed]
            if remaining:
                return ReflectionDecision(
                    action=ReflectionAction.CONTINUE,
                    reason=f"{len(remaining)} step(s) remain in the plan.",
                )
            return ReflectionDecision(
                action=ReflectionAction.COMPLETE,
                reason="All plan steps completed successfully.",
            )

        failed_result = self._find_failed_tool_result(result)
        if failed_result is None:
            
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=f"Step '{result.failed_step}' failed before producing a result "
                       f"(likely a missing or misconfigured tool).",
            )

        category = self._classify_error(failed_result)

        if category == "not_found":
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=failed_result.error,
                referenced_tool=failed_result.tool_name,
            )
        if category == "validation":
            return ReflectionDecision(
                action=ReflectionAction.ASK_USER,
                reason=failed_result.error,
                ask_user_message=f"I need more information: {failed_result.error}",
                referenced_tool=failed_result.tool_name,
            )
        if category == "permission":
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=failed_result.error,
                referenced_tool=failed_result.tool_name,
            )
        if category == "timeout":
            return ReflectionDecision(
                action=ReflectionAction.RETRY,
                reason=failed_result.error,
                retry_step=result.failed_step,
                referenced_tool=failed_result.tool_name,
            )

       
        return None

    async def _llm_check(self, context: RuntimeContext, result: ExecutionResult) -> ReflectionDecision:
        failed_result = self._find_failed_tool_result(result)
        remaining = [s.name for s in context.state.plan if not s.completed]
        available_tools = context.tool_executor.registry.list_names()

        prompt_context = ReflectionPromptContext(
            query=context.state.query,
            failed_step=result.failed_step,
            error=failed_result.error if failed_result else None,
            remaining_step_names=remaining,
            available_tool_names=list(available_tools),
        )

        try:
            decision = await self._llm_reflector.decide(prompt_context)
        except Exception as exc:
            # defense in depth — even a misbehaving custom LLMReflector
            # implementation can't crash the runtime or leave no decision
            logger.error("LLM reflector raised unexpectedly: %s", exc)
            return ReflectionDecision(
                action=ReflectionAction.ABORT,
                reason=f"LLM reflector raised an exception: {exc}",
                source="fallback",
            )

       
        if decision.source != "fallback":
            decision.source = "llm"
        return decision

    def _validate(self, context: RuntimeContext, decision: ReflectionDecision) -> ReflectionDecision:
        if decision.referenced_tool is not None:
            if not context.tool_executor.registry.has(decision.referenced_tool):
                return ReflectionDecision(
                    action=ReflectionAction.ABORT,
                    reason=f"Reflection referenced unknown tool '{decision.referenced_tool}', "
                           f"which is not registered — aborting rather than acting on it.",
                    source=decision.source,
                )

        if decision.action == ReflectionAction.RETRY:
            step_names = {s.name for s in context.state.plan}
            if decision.retry_step not in step_names:
                return ReflectionDecision(
                    action=ReflectionAction.ABORT,
                    reason=f"RETRY referenced unknown step '{decision.retry_step}' — "
                           f"aborting rather than acting on it.",
                    source=decision.source,
                )

        return decision

    @staticmethod
    def _find_failed_tool_result(result: ExecutionResult) -> ToolResult | None:
        
        if not result.tool_results:
            return None
        last = result.tool_results[-1]
        return None if last.success else last

    @staticmethod
    def _classify_error(failed_result: ToolResult) -> str:
        
        mapping = {
            ToolErrorType.NOT_FOUND: "not_found",
            ToolErrorType.VALIDATION: "validation",
            ToolErrorType.PERMISSION: "permission",
            ToolErrorType.TIMEOUT: "timeout",
            ToolErrorType.EXECUTION: "execution",
        }
        return mapping.get(failed_result.error_type, "execution")