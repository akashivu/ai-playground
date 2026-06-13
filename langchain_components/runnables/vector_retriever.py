from langchain_core.runnables import RunnableLambda
from core.dependencies import retrieval_service


def retrieve(payload: dict) -> list[dict]:
    """Performs vector retrieval for the given query and collection."""
    return retrieval_service.search(
        query=payload["query"],
        collection=payload.get("collection"),
    )


vector_retriever = RunnableLambda(retrieve)