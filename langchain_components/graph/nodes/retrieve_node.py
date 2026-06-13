from langchain_components.runnables.hybrid_search_pipeline import hybrid_search_pipeline


def retrieve_node(state: dict) -> dict:
    """Retrieves relevant chunks from the domain knowledge base."""
    results = hybrid_search_pipeline.invoke({
        "query": state.get("rewritten_query") or state["question"],
        "collection": state.get("collection"),
    })
    return {
        "context": "\n\n".join(r["chunk"] for r in results),
        "retrieval_successful": len(results) > 0,
    }