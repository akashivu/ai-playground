from fastapi import APIRouter

from core.dependencies import (knowledge_base_service,)
from models.document_model import (DocumentRequest,)

router = APIRouter()
@router.post("/documents")
def add_document(request: DocumentRequest,):

    document = (knowledge_base_service.add_document(request.document_id,request.name,request.collection,))

    return document

@router.get("/documents")
def list_documents():

    return (knowledge_base_service.list_documents())

@router.delete("/documents/{document_id}")
def delete_document(document_id: str,):

    return (knowledge_base_service.delete_document(document_id))