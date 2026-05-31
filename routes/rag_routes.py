from models.rag_model import RAGRequest
from services.rag_service import RAGService
from fastapi import APIRouter

router= APIRouter()

rag_service = None


@router.post("/ask")
def ask_question(request: RAGRequest,):

    answer = (rag_service.answer_question(request.question))

    return {"question": request.question,"answer": answer,}