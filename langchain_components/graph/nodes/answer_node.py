from langchain_components.chains.rag_answer_chain import rag_answer_chain


def answer_node(state: dict) -> dict:
    """Generates an answer using retrieved context."""
    answer = rag_answer_chain.invoke({
        "question": state["question"],
        "context": state.get("context", ""),
    })
    return {"answer": answer}