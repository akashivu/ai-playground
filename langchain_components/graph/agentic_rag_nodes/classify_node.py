from langchain_components.chains.retrieval_classifier_chain import retrieval_classifier_chain


def classify_node(state: dict) -> dict:
    """Determines whether retrieval is required for the given question."""
    result = retrieval_classifier_chain.invoke({"question": state["question"]})
    return {"requires_retrieval": result.get("requires_retrieval", False)}