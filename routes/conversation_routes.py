from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from auth.schemas import CurrentUser
from auth.optional_auth import get_current_or_guest_user

from core.dependencies import conversation_store

router = APIRouter(
    prefix="",
    tags=["Conversation"],
)


@router.get("/sessions")
async def get_sessions(
    current_user: CurrentUser = Depends(get_current_or_guest_user),
):
    sessions = conversation_store.get_user_sessions(
        user_id=str(current_user.user_id),
    )

    return {
        "sessions": sessions,
    }


@router.get("/sessions/{session_id}")
async def get_conversation(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_or_guest_user),
):
    if not conversation_store.session_exists(
        user_id=str(current_user.user_id),
        session_id=session_id,
    ):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    messages = conversation_store.get_session(
        user_id=str(current_user.user_id),
        session_id=session_id,
    )

    return {
        "session_id": session_id,
        "messages": messages,
    }


@router.delete("/sessions/{session_id}")
async def delete_conversation(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_or_guest_user),
):
    if not conversation_store.session_exists(
        user_id=str(current_user.user_id),
        session_id=session_id,
    ):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    conversation_store.delete_session(
        user_id=str(current_user.user_id),
        session_id=session_id,
    )

    return {
        "message": "Conversation deleted successfully.",
    }