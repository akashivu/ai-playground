
from core.dependencies import hybrid_retrieval_service


def retrieve_node(state: dict) -> dict:
    """Retrieves relevant chunks and builds context string."""
    results = hybrid_retrieval_service.search(state["question"])
    context = "\n\n".join(r["chunk"] for r in results)
    return {
        "context": context,
        "retrieval_successful": len(results) > 0,
    }