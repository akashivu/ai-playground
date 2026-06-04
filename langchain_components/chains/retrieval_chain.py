from langchain_core.runnables import RunnableLambda
from langchain_components.runnables.hybrid_search_pipeline import hybrid_search_pipeline
from langchain_components.chains.rag_answer_chain import rag_answer_chain


def retrieval_workflow(question: str) -> str:
    """Retrieves relevant chunks and generates an answer for the given question."""
    results = hybrid_search_pipeline.invoke(question)
    context = "\n\n".join(item["chunk"] for item in results)
    return rag_answer_chain.invoke({"question": question, "context": context})


retrieval_chain = RunnableLambda(retrieval_workflow)