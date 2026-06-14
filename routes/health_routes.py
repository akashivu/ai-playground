from fastapi import APIRouter
from core.dependencies import vector_store, conversation_store

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Returns platform health status for monitoring systems."""
    return {
        "status": "healthy",
        "vector_store_loaded": len(vector_store.metadata) > 0,
        "knowledge_chunks": len(vector_store.metadata),
        "conversation_store": conversation_store.__class__.__name__,
    }