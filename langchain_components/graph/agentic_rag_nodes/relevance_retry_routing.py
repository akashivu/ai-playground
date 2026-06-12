
def route_relevance_or_retry(state: dict) -> str:
    """Routes to answer, retry rewrite, or fallback based on relevance and retry count."""
    if state.get("retrieval_relevant", False):
        return "answer"
    if state.get("retry_count", 0) < state.get("max_retries", 1):
        return "retry_rewrite"
    return "fallback"