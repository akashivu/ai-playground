from fastapi import APIRouter

from models.hybrid_search_model import (HybridSearchRequest,)

from core.dependencies import (hybrid_retrieval_service,)

router = APIRouter()


@router.post("/hybrid-search")
def hybrid_search(request: HybridSearchRequest,):

    results = (hybrid_retrieval_service.search(request.query))

    return {"query": request.query,"results": results,}