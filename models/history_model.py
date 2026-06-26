from datetime import datetime

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    """
    Summary information for a conversation.
    Used when listing a user's conversations.
    """

    session_id: str

    created_at: datetime

    last_active: datetime


class ConversationMessage(BaseModel):
    """
    Represents a single chat message.
    """

    role: str

    content: str


class ConversationHistory(BaseModel):
    """
    Represents a complete conversation.
    """

    session_id: str

    messages: list[ConversationMessage] = Field(default_factory=list)


class ConversationListResponse(BaseModel):
    """
    Response returned by GET /history/sessions
    """

    conversations: list[ConversationSummary] = Field(default_factory=list)