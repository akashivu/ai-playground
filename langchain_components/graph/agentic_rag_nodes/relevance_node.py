from langchain_components.chains.retrieval_relevance_chain import retrieval_relevance_chain


def relevance_node(state: dict) -> dict:
    """Evaluates whether retrieved context is relevant to the question."""
    result = retrieval_relevance_chain.invoke({
        "question": state["question"],
        "context": state["context"],
    })
    return {"retrieval_relevant": result.get("relevant", False)}