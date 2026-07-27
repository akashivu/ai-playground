from __future__ import annotations

import time
from typing import Any, Callable

from langchain_components.agents.base_agent import BaseAgent
from langchain_components.agents.context import AgentContext
from langchain_components.agents.exceptions import AgentNotFoundError
from langchain_components.agents.registry import AgentRegistry
from langchain_components.agents.registry import (
    agent_registry as default_agent_registry,
)
from langchain_components.agents.result import AgentResult
from langchain_components.conversation.context import ConversationContext
from langchain_components.conversation.exceptions import AgentResolutionError
from langchain_components.conversation.result import ConversationResult
from langchain_components.memory.base_memory import BaseMemory
from langchain_components.memory.context import MemoryContext
from langchain_components.memory.result import MemoryEntry, MemoryResult

AgentResolver = Callable[[dict[str, Any], ConversationContext], str]


def _default_agent_resolver(
    request: dict[str, Any], context: ConversationContext
) -> str:
    agent_name = request.get("agent_name") or request.get("intent")
    if not agent_name:
        raise AgentResolutionError(
            "request has no 'agent_name' or 'intent' and no IntentRouter is configured"
        )
    return agent_name


class ConversationManager:
    def __init__(
        self,
        memory: BaseMemory | None = None,
        agent_registry: AgentRegistry | None = None,
        agent_resolver: AgentResolver | None = None,
    ) -> None:
        self.memory = memory
        self.agent_registry = agent_registry or default_agent_registry
        self.agent_resolver = agent_resolver or _default_agent_resolver

    async def handle_message(
        self, request: dict[str, Any], context: ConversationContext
    ) -> ConversationResult:
        start = time.perf_counter()
        warnings: list[str] = []

        memory_result = await self._load_memory(context, warnings)

        try:
            agent_name = self.agent_resolver(request, context)
        except AgentResolutionError as exc:
            return self._failure(str(exc), start, warnings)

        try:
            agent: BaseAgent = self.agent_registry.get(agent_name)
        except AgentNotFoundError as exc:
            return self._failure(str(exc), start, warnings)

        agent_context = self._build_agent_context(context, memory_result)
        agent_result = await agent.run(request, agent_context)

        await self._save_turn(context, request, agent_result, warnings)

        return ConversationResult(
            success=agent_result.success,
            response=agent_result.response,
            agent_name=agent_name,
            agent_result=agent_result,
            memory_result=memory_result,
            error=agent_result.error,
            execution_time_ms=(time.perf_counter() - start) * 1000,
            metadata={"warnings": warnings} if warnings else {},
        )

    async def _load_memory(
        self, context: ConversationContext, warnings: list[str]
    ) -> MemoryResult | None:
        if self.memory is None:
            return None
        try:
            return await self.memory.load(self._build_memory_context(context))
        except (
            Exception
        ) as exc:  # noqa: BLE001 - memory must never break the conversation
            warnings.append(f"memory load failed: {exc}")
            return None

    async def _save_turn(
        self,
        context: ConversationContext,
        request: dict[str, Any],
        agent_result: AgentResult,
        warnings: list[str],
    ) -> None:
        if self.memory is None:
            return
        entries = [MemoryEntry(content=request.get("message", ""), role="user")]
        if agent_result.response:
            entries.append(MemoryEntry(content=agent_result.response, role="assistant"))
        try:
            await self.memory.save(self._build_memory_context(context), entries)
        except (
            Exception
        ) as exc:  # noqa: BLE001 - memory must never break the conversation
            warnings.append(f"memory save failed: {exc}")

    def _build_memory_context(self, context: ConversationContext) -> MemoryContext:
        return MemoryContext(
            user_id=context.user_id,
            session_id=context.session_id,
            conversation_id=context.conversation_id,
            trace_id=context.trace_id,
            metadata=context.metadata,
        )

    def _build_agent_context(
        self, context: ConversationContext, memory_result: MemoryResult | None
    ) -> AgentContext:
        history = (
            [entry.model_dump() for entry in memory_result.entries]
            if memory_result
            else []
        )
        return AgentContext(
            user_id=context.user_id,
            session_id=context.session_id,
            conversation_history=history,
            metadata=context.metadata,
            trace_id=context.trace_id,
        )

    def _failure(
        self, error: str, start: float, warnings: list[str]
    ) -> ConversationResult:
        return ConversationResult.fail(
            error=error,
            execution_time_ms=(time.perf_counter() - start) * 1000,
            metadata={"warnings": warnings} if warnings else {},
        )