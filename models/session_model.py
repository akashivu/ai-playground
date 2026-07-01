from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: str


class ConversationMessage(BaseModel):
    role: str
    content: str


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: list[ConversationMessage]

class DeleteSessionResponse(BaseModel):
    status: str
    session_id: str
