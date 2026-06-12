from langchain_components.chains.query_rewrite_chain import query_rewrite_chain


def retry_rewrite_node(state: dict) -> dict:
    """Rewrites the query to improve retrieval on retry."""
    rewritten = query_rewrite_chain.invoke({
        "history": "",
        "question": state["question"],
    })
    return {
        "question": rewritten,
        "retry_count": state.get("retry_count", 0) + 1,
    }