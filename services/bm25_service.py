from rank_bm25 import BM25Okapi


class BM25Service:
    """BM25 keyword search service with metadata filtering."""

    def __init__(self) -> None:
        self.metadata: list[dict] = []
        self.bm25: BM25Okapi | None = None

    def _rebuild_index(self) -> None:
        """Rebuilds the BM25 index from current metadata."""
        tokenized = [meta["text"].lower().split() for meta in self.metadata]
        self.bm25 = BM25Okapi(tokenized)

    def build_index(self, metadata: list[dict]) -> None:
        """Builds BM25 index from a list of metadata dicts."""
        self.metadata = metadata
        self._rebuild_index()

    def add_documents(self, metadata: list[dict]) -> None:
        """Adds new documents and rebuilds the index."""
        self.metadata.extend(metadata)
        self._rebuild_index()

    def search(
        self,
        query: str,
        top_k: int = 3,
        collection: str | None = None,
    ) -> list[dict]:
        """Returns top-k BM25 results with optional collection filtering."""
        if self.bm25 is None:
            raise RuntimeError("BM25 index not built. Call build_index() first.")

        scores = self.bm25.get_scores(query.lower().split())
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for idx in top_indices:
            if idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            if collection and meta.get("collection") != collection:
                continue

            results.append({
                "chunk": meta["text"],
                "source": meta["source"],
                "document_id": meta["document_id"],
                "collection": meta["collection"],
                "score": float(scores[idx]),
            })

            if len(results) == top_k:
                break

        return results