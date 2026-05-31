from fastapi import APIRouter

from models.search_model import (
    SearchRequest,
)

from services.retrieval_service import (
    RetrievalService,
)

router = APIRouter()

retrieval_service = None


@router.post("/search")
def semantic_search(
    request: SearchRequest,
):

    results = retrieval_service.search(
        request.query,
        request.top_k,
    )

    return {
        "query": request.query,
        "results": results,
    }