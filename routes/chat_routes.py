from fastapi import APIRouter, HTTPException, Depends
from models.chat_model import ChatRequest, ChatResponse
from services.rate_limit_service import rate_limit_service
from langchain_components.conversation.conversation_manager import (
    conversation_manager,
)
from utils.logger import logger
from auth.schemas import CurrentUser
from auth.optional_auth import get_current_or_guest_user

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: CurrentUser = Depends(get_current_or_guest_user),
) -> ChatResponse:

    
    if current_user.is_guest and body.guest_id:
        current_user.user_id = body.guest_id
        logger.info(
            "CHAT user=%s session=%s",
            current_user.user_id,
            body.session_id,
        )

    if not rate_limit_service.allow_request(
        user_id=str(current_user.user_id),
        session_id=body.session_id,
    ):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
        )

    try:
        response = conversation_manager.process_message(
            current_user=current_user,
            session_id=body.session_id,
            question=body.question,
        )

        return ChatResponse(
            session_id=response.session_id,
            answer=response.answer,
            intent=response.intent,
            completed=response.completed,
            metadata=response.metadata,
        )

    except Exception:
        logger.exception("Chat endpoint failed")
        raise HTTPException(status_code=500,detail="Internal server error.",)