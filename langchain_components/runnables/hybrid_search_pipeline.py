from langchain_core.runnables import RunnableLambda
from core.dependencies import hybrid_retrieval_service


def hybrid_search(payload: dict) -> list[dict]:
    """Performs hybrid retrieval for the given query and collection."""
    return hybrid_retrieval_service.search(
        query=payload["query"],
        collection=payload.get("collection"),
    )


hybrid_search_pipeline = RunnableLambda(hybrid_search)