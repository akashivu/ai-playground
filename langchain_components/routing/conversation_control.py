"""
Router for classifying conversation-control signals during an active booking.

Usage:
    from langchain_components.routing.conversation_control import classify_conversation_control

    control = classify_conversation_control(question, llm=my_llm)

    if control == ConversationControl.CANCEL:
        ...
"""

from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from langchain_components.routing.conversation_control_prompt import (
    CONVERSATION_CONTROL_PROMPT,
    ConversationControl,
)


class ConversationControlResult(BaseModel):
    """Structured output schema for the classifier."""

    control: ConversationControl = Field(
        description=(
            "The conversation control signal detected in the user's message: "
            "NONE, CANCEL, PAUSE, RESUME, or INTERRUPT."
        )
    )


def _get_default_llm() -> BaseChatModel:
    """
    Lazily build a default LLM if the caller doesn't provide one.

    NOTE: Replace this with however your project constructs its shared LLM client
    if one already exists (e.g. a project-wide `get_llm()` factory) — this is just
    a safe fallback so the module works standalone. Uses settings.OPENAI_MODEL to
    match the rest of the app (see ConversationManager / cost_estimation_service).
    """
    from langchain_openai import ChatOpenAI
    from config.settings import settings

    return ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)


@lru_cache(maxsize=1)
def _default_chain():
    llm = _get_default_llm()
    structured_llm = llm.with_structured_output(ConversationControlResult)
    return CONVERSATION_CONTROL_PROMPT | structured_llm


def classify_conversation_control(
    question: str,
    llm: BaseChatModel | None = None,
) -> ConversationControl:
    """
    Classify a user message into a ConversationControl signal.

    This should only be called when there is an active booking in progress —
    see ConversationManager for the routing logic that decides when to invoke it.

    Args:
        question: The user's latest message.
        llm: Optional chat model to use. If omitted, a cached default is used.

    Returns:
        ConversationControl: One of NONE, CANCEL, PAUSE, RESUME, INTERRUPT.
    """
    if not question or not question.strip():
        return ConversationControl.NONE

    if llm is not None:
        structured_llm = llm.with_structured_output(ConversationControlResult)
        chain = CONVERSATION_CONTROL_PROMPT | structured_llm
    else:
        chain = _default_chain()

    try:
        result: ConversationControlResult = chain.invoke({"question": question})
        return result.control
    except Exception:
        # Fail safe: never let a classifier error break an active booking flow.
        # Defaulting to NONE means the message falls through to normal booking
        # slot-filling logic rather than incorrectly cancelling/interrupting.
        return ConversationControl.NONE