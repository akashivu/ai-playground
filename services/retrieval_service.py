import numpy as np

from embeddings.embedding_service import get_embedding

class RetrievalService:
    def __init__ (self, vectore_store):
        self.vector_store=self.vector_store

    def search(self, query: str, top_k : int=3):
        query_embedding=get_embedding(query)
        query_vector = np.array([query_embedding], dtype=np.float32)

        result=self.vector_store.search(query_vector, top_k)

        return result