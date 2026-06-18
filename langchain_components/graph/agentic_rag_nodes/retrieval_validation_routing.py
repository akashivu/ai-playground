def route_after_retrieval_validation(state: dict) -> str:
    """Skips the LLM relevance check entirely if pre-filter already failed."""
    if not state.get("retrieval_successful", False):
        return "retry_or_fallback"
    return "relevance"