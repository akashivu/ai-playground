from fastapi import APIRouter

from models.search_model import (SearchRequest,)
from core.dependencies import (retrieval_service,)


router = APIRouter()

@router.post("/search")
def semantic_search(request: SearchRequest,):

    results = retrieval_service.search(request.query,request.top_k,)

    return {"query": request.query,"results": results,}