from fastapi import APIRouter, Depends, HTTPException

from auth.optional_auth import get_current_or_guest_user
from auth.schemas import CurrentUser
from models.history_model import (
    ConversationHistory,
    ConversationListResponse,
    ConversationMessage,
    ConversationSummary,
)
from services.history_service import history_service

router = APIRouter(
    prefix="/history",
    tags=["Conversation History"],
)


@router.get(
    "/sessions",
    response_model=ConversationListResponse,
)
async def list_sessions(
    current_user: CurrentUser = Depends(
        get_current_or_guest_user,
    ),
) -> ConversationListResponse:
    """
    Returns all conversations belonging to the current user.
    """

    sessions = history_service.list_sessions(
        user_id=current_user.user_id,
    )

    return ConversationListResponse(
        conversations=[
            ConversationSummary(**session)
            for session in sessions
        ]
    )


@router.get(
    "/{session_id}",
    response_model=ConversationHistory,
)
async def get_history(
    session_id: str,
    current_user: CurrentUser = Depends(
        get_current_or_guest_user,
    ),
) -> ConversationHistory:
    """
    Returns the complete conversation.
    """

    messages = history_service.get_session(
        user_id=current_user.user_id,
        session_id=session_id,
    )

    if not messages:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return ConversationHistory(
        session_id=session_id,
        messages=[
            ConversationMessage(**message)
            for message in messages
        ],
    )


@router.delete(
    "/{session_id}",
    status_code=204,
)
async def delete_history(
    session_id: str,
    current_user: CurrentUser = Depends(
        get_current_or_guest_user,
    ),
) -> None:
    """
    Deletes a conversation.
    """

    history_service.delete_session(
        user_id=current_user.user_id,
        session_id=session_id,
    )