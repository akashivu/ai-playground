from embeddings.vector_store import (VectorStore,)

from services.retrieval_service import (RetrievalService,)

from services.rag_service import (RAGService,)

from services.conversational_rag_service import (ConversationalRAGService,)

from services.reranking_service import (RerankingService,)

from services.document_service import (DocumentService,)

from services.knowledge_base_service import (KnowledgeBaseService,)

from services.bm25_service import (BM25Service,)

from services.hybrid_retrieval_service import (HybridRetrievalService,)

import os

vector_store = VectorStore(dimension=1536)
if os.path.exists("faiss.index"):
    vector_store.load_index("faiss.index")

if os.path.exists("metadata.json"):
    vector_store.load_metadata("metadata.json")
retrieval_service = (RetrievalService(vector_store))
bm25_service = (BM25Service())
if vector_store.metadata:

    bm25_service.add_documents([item["text"] for item in vector_store.metadata])
rag_service = (RAGService(retrieval_service))
reranking_service = (RerankingService())
hybrid_retrieval_service = (HybridRetrievalService(retrieval_service,bm25_service,reranking_service,))
conversational_rag_service = (ConversationalRAGService(retrieval_service,reranking_service,hybrid_retrieval_service,))
document_service = (DocumentService(vector_store,bm25_service,))
knowledge_base_service = (KnowledgeBaseService())
