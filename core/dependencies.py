from embeddings.vector_store import (VectorStore,)

from services.retrieval_service import (RetrievalService,)

from services.rag_service import (RAGService,)

from services.conversational_rag_service import (ConversationalRAGService,)

from services.reranking_service import (RerankingService,)

from services.knowledge_ingestion_service import (KnowledgeIngestionService,)

from services.knowledge_base_service import (KnowledgeBaseService,)

from services.bm25_service import (BM25Service,)

from services.hybrid_retrieval_service import (HybridRetrievalService,)

import os
from langchain_components.memory.persistent_conversation_store import PersistentConversationStore

from services.evaluation_service import (EvaluationService,)
from services.benchmark_service import (BenchmarkService,)
vector_store = VectorStore(dimension=1536)
if os.path.exists("faiss.index"):
    vector_store.load_index("faiss.index")

if os.path.exists("metadata.json"):
    vector_store.load_metadata("metadata.json")
retrieval_service = (RetrievalService(vector_store))
bm25_service = (BM25Service())
if vector_store.metadata:

    bm25_service.add_documents(vector_store.metadata)
rag_service = (RAGService(retrieval_service))
reranking_service = (RerankingService())
hybrid_retrieval_service = (HybridRetrievalService(retrieval_service,bm25_service,reranking_service,))
evaluation_service = (EvaluationService())
conversational_rag_service = (ConversationalRAGService(retrieval_service,reranking_service,hybrid_retrieval_service,
                                                       evaluation_service,))
knowledge_ingestion_service = (KnowledgeIngestionService(vector_store,bm25_service,))
knowledge_base_service = (KnowledgeBaseService())
benchmark_service = (BenchmarkService(conversational_rag_service))
conversation_store = PersistentConversationStore(db_path="data/conversations.db")