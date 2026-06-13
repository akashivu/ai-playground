import numpy as np
from embeddings.embedding_service import get_embedding
from embeddings.vector_store import VectorStore


class RetrievalService:
    """Handles query embedding and vector store retrieval."""

    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        top_k: int = 3,
        collection: str | None = None,
    ) -> list[dict]:
        """Embeds the query and searches the vector store."""
        query_vector = np.array([get_embedding(query)], dtype=np.float32)
        return self.vector_store.search(query_vector, top_k, collection=collection)