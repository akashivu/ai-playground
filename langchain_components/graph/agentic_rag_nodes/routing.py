def route_retrieval(state: dict) -> str:
    """Routes to retrieval or direct answer based on classification."""
    if state.get("requires_retrieval", False):
        return "retrieve"
    return "direct_answer"