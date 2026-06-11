from langchain_core.tools import tool
from core.dependencies import hybrid_retrieval_service

@tool
def knowledge_base_search(query: str) -> str:
    """Searches the knowledge base and returns relevant document chunks."""
    results = hybrid_retrieval_service.search(query)

    if not results:
        return "No relevant documents found."

    return "\n\n".join(result["chunk"] for result in results)