import json
import faiss
import numpy as np


class VectorStore:
    """FAISS-backed vector store with metadata filtering and persistence."""

    def __init__(self, dimension: int) -> None:
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: list[dict] = []

    def add_documents(self, embeddings: list, metadata: list[dict]) -> None:
        """Adds embeddings and associated metadata to the store."""
        vectors = np.array(embeddings, dtype=np.float32)
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 3,
        collection: str | None = None,
        document_id: str | None = None,
    ) -> list[dict]:
        """Searches for top-k results with optional collection and document filtering."""
        distances, indices = self.index.search(query_vector, k * 3)
        results = []

        for position, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            if collection and meta["collection"] != collection:
                continue
            if document_id and meta["document_id"] != document_id:
                continue

            results.append({
                "chunk": meta["text"],
                "source": meta["source"],
                "document_id": meta["document_id"],
                "collection": meta["collection"],
                "score": float(distances[0][position]),
            })

            if len(results) == k:
                break

        return results

    def save_index(self, path: str) -> None:
        """Saves the FAISS index to disk."""
        faiss.write_index(self.index, path)

    def load_index(self, path: str) -> None:
        """Loads a FAISS index from disk."""
        self.index = faiss.read_index(path)

    def save_metadata(self, path: str) -> None:
        """Saves metadata to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)

    def load_metadata(self, path: str) -> None:
        """Loads metadata from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)