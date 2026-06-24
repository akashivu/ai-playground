from fastapi import APIRouter, HTTPException
from models.chat_model import ChatRequest, ChatResponse
from core.dependencies import conversation_store
from langchain_components.routing.intent_router import route_question
from services.recommendation_session_service import recommendation_session_service
from services.booking_session_service import (booking_session_service,)
from utils.logger import logger

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Processes a chat message with session memory and recommendation handoff."""
    try:
        history = conversation_store.get_messages(body.session_id)

        booking_details = booking_session_service.get_booking(body.session_id)

        previous_recommendation = recommendation_session_service.get(body.session_id)

        state = {
            "session_id": body.session_id,
            "question": body.question,
            "history": history,
            "booking_details": booking_details,
            "recommendation_details": previous_recommendation,
        }

        result = route_question(state)
        answer = result.get("answer", "I was unable to generate a response.")

        if "recommendation_details" in result:
            recommendation_session_service.save(
                body.session_id,
                result["recommendation_details"],
            )

        if result.get("completed"):
            recommendation_session_service.clear(body.session_id)

        conversation_store.add_message(body.session_id, "user", body.question)
        conversation_store.add_message(body.session_id,"assistant",answer,)

        return ChatResponse(session_id=body.session_id, answer=answer)

    except Exception as e:
        logger.exception("Chat endpoint failed")
        raise HTTPException(status_code=500, detail="Internal server error.")