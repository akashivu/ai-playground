from langchain_components.knowledge.pricing_store import (PRICING_DOCUMENTS,)
from core.dependencies import (vector_store,bm25_service,)
from embeddings.embedding_service import (get_embedding,)
from config.storage_config import (FAISS_INDEX_PATH,METADATA_PATH,)

def ingest_pricing() -> None:
    embeddings = []
    metadata = []

    for doc in PRICING_DOCUMENTS:
        embeddings.append(
            get_embedding(doc["text"])
        )

        metadata.append({
            "text": doc["text"],
            "source": doc["source"],
            "document_id": doc["document_id"],
            "collection": doc["collection"],})
    vector_store.add_documents(embeddings,metadata,)
    vector_store.save_index(FAISS_INDEX_PATH,)
    vector_store.save_metadata(METADATA_PATH,)
    bm25_service.add_documents(metadata)
    print(f"Ingested {len(PRICING_DOCUMENTS)} pricing documents.")


if __name__ == "__main__":
    ingest_pricing()