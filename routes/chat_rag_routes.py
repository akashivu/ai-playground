from fastapi import APIRouter

from models.chat_rag_model import (ChatRAGRequest,)

from core.dependencies import (conversational_rag_service,)

router = APIRouter()


@router.post("/chat-rag")
async def chat_rag(request: ChatRAGRequest,):

    answer = await (conversational_rag_service.answer_question(request.messages))

    return {"answer": answer,}