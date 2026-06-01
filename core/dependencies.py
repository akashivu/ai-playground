from embeddings.vector_store import (VectorStore,)

from services.retrieval_service import (RetrievalService,)

from services.rag_service import (RAGService,)

vector_store = VectorStore(dimension=1536)
retrieval_service = (RetrievalService(vector_store))
rag_service = (RAGService(retrieval_service))