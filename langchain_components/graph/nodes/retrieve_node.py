from langchain_components.runnables.hybrid_search_pipeline import hybrid_search_pipeline
from services.retrieval_validator import RetrievalValidator


def retrieve_node(state: dict) -> dict:
    """Retrieves chunks and performs a cheap validation before the relevance LLM is called."""
    results = hybrid_search_pipeline.invoke({
        "query": state.get("rewritten_query") or state["question"],
        "collection": state.get("collection"),
    })

    validation = RetrievalValidator.validate(results)

    if not validation.is_valid:
        return {
            "results": [],
            "context": "",
            "retrieval_successful": False,
            "retrieval_failure_reason": validation.reason,
        }

    return {
        "results": results,
        "context": "\n\n".join(r["chunk"] for r in results),
        "retrieval_successful": True,
    }