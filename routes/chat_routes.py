from fastapi import APIRouter, HTTPException
from models.chat_model import ChatRequest, ChatResponse
from core.dependencies import conversation_store
from langchain_components.routing.intent_router import route_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Processes a chat message within a session and returns an answer."""
    try:
        history = conversation_store.get_messages(body.session_id)

        state = {
            "session_id": body.session_id,
            "question": body.question,
            "history": history,
        }

        result = route_question(state)
        answer = result.get("answer", "I was unable to generate a response.")

        conversation_store.add_message(body.session_id, "user", body.question)
        conversation_store.add_message(body.session_id, "assistant", answer)

        return ChatResponse(session_id=body.session_id, answer=answer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))