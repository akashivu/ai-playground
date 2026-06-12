def fallback_node(state: dict) -> dict:
    """Returns a fallback answer when retrieval yields no results."""
    return {"answer": "I do not have enough information to answer this question."}