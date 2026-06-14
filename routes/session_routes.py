from fastapi import APIRouter, HTTPException
from models.session_model import (
    SessionResponse,
    SessionMessagesResponse,
    DeleteSessionResponse,
)
from langchain_components.memory.session_manager import create_session
from core.dependencies import conversation_store

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
def create_new_session() -> SessionResponse:
    """Creates a new conversation session."""
    return SessionResponse(session_id=create_session())


@router.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
def get_messages(session_id: str) -> SessionMessagesResponse:
    """Returns full conversation history for a session."""
    if not conversation_store.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    messages = conversation_store.get_session(session_id)
    return SessionMessagesResponse(
        session_id=session_id,
        messages=messages,
        total=len(messages),
    )


@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
def delete_session(session_id: str) -> DeleteSessionResponse:
    """Deletes a session and clears its conversation history."""
    if not conversation_store.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    conversation_store.clear_session(session_id)
    return DeleteSessionResponse(status="deleted", session_id=session_id)