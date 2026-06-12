def route_relevance(state: dict) -> str:
    """Routes to answer or fallback based on retrieval relevance."""
    if state.get("retrieval_relevant", False):
        return "answer"
    return "fallback"