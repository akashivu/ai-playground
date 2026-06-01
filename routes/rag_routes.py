from models.rag_model import RAGRequest
from fastapi import APIRouter
from core.dependencies import (rag_service,)
router= APIRouter()

@router.post("/ask")
def ask_question(request: RAGRequest,):

    answer = (rag_service.answer_question(request.question))

    return {"question": request.question,"answer": answer,}