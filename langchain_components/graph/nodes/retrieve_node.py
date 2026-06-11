from langchain_components.runnables.hybrid_search_pipeline import (hybrid_search_pipeline,)

def retrieve_node(state,):
    """Retrieves relevant context for the rewritten query."""
    results = (hybrid_search_pipeline.invoke(state["rewritten_query"]))
    context = "\n\n".join(item.get("chunk","",)for item in results)
    return {"context":context}