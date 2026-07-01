import os
import uuid
from datetime import datetime
from embeddings.embedding_service import get_embedding
from loaders.pdf_loader import load_pdf
from utils.text_cleaner import clean_text
from utils.text_splitter import split_chunks
from utils.logger import logger
from config.storage_config import FAISS_INDEX_PATH, METADATA_PATH

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


class KnowledgeIngestionService:
    """Handles document ingestion into vector store and BM25 indexes."""

    def __init__(self, vector_store, bm25_service) -> None:
        self.vector_store = vector_store
        self.bm25_service = bm25_service

    def ingest_document(self, file_path: str, collection: str, document_id: str | None = None, persist: bool = True) -> dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = os.path.splitext(file_path)[1].lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        document_id = document_id or str(uuid.uuid4())
        logger.info(f"Ingesting '{file_path}' into collection '{collection}'")

        chunks = self._extract_chunks(file_path=file_path, extension=extension)
        if not chunks:
            logger.warning(f"No content extracted from '{file_path}'")
            return {"status": "warning", "document_id": document_id, "collection": collection, "chunks": 0}

        embeddings = []
        metadata = []

        for index, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            try:
                embedding = get_embedding(chunk)
            except Exception as e:
                logger.error(f"Failed to generate embedding for chunk {index}: {e}")
                continue

            embeddings.append(embedding)
            metadata.append({
                "text": chunk,
                "source": os.path.basename(file_path),
                "document_id": f"{document_id}_{index}",
                "collection": collection,
                "document_type": extension.replace(".", ""),
                "chunk_index": index,
                "ingested_at": datetime.utcnow().isoformat(),
            })

        if not embeddings:
            return {"status": "error", "document_id": document_id, "collection": collection, "chunks": 0}

        self.vector_store.add_documents(embeddings, metadata)
        self.bm25_service.add_documents(metadata)

        if persist:
            self.vector_store.save_index(FAISS_INDEX_PATH)
            self.vector_store.save_metadata(METADATA_PATH)

        logger.info(f"Successfully ingested {len(metadata)} chunks from '{file_path}'")
        return {"status": "success", "document_id": document_id, "collection": collection, "chunks": len(metadata)}

    def ingest_directory(self, directory: str, collection: str, persist: bool = True) -> dict:
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Directory not found: {directory}")

        total_chunks = 0
        total_documents = 0

        for filename in os.listdir(directory):
            extension = os.path.splitext(filename)[1].lower()
            if extension not in SUPPORTED_EXTENSIONS:
                continue
            file_path = os.path.join(directory, filename)
            try:
                result = self.ingest_document(file_path=file_path, collection=collection, persist=False)
                if result["chunks"] > 0:
                    total_documents += 1
                    total_chunks += result["chunks"]
            except Exception as e:
                logger.error(f"Failed to ingest {filename}: {e}")

        if persist and total_chunks > 0:
            self.vector_store.save_index(FAISS_INDEX_PATH)
            self.vector_store.save_metadata(METADATA_PATH)

        logger.info(f"Directory ingestion complete. Documents={total_documents}, Chunks={total_chunks}")
        return {"status": "success", "collection": collection, "documents": total_documents, "chunks": total_chunks}

    def _extract_chunks(self, file_path: str, extension: str) -> list[str]:
        if extension == ".pdf":
            return self._read_pdf(file_path)
        return self._read_text(file_path)

    def _read_text(self, file_path: str) -> list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return split_chunks(clean_text(text))

    def _read_pdf(self, file_path: str) -> list[str]:
        return split_chunks(clean_text(load_pdf(file_path)))
