from services.retrieval_service import (RetrievalService,)

from services.bm25_service import (BM25Service,)


class HybridRetrievalService:
    """Combines vector search and BM25 for hybrid retrieval."""

    def __init__(self, retrieval_service: RetrievalService, bm25_service: BM25Service) -> None:
        self.retrieval_service = retrieval_service
        self.bm25_service = bm25_service

    def search(
        self,
        query: str,
        top_k: int = 3,
        collection: str | None = None,
    ) -> list[dict]:
        """Performs hybrid retrieval with optional collection filtering."""
        vector_results = self.retrieval_service.search(
            query=query,
            top_k=top_k,
            collection=collection,
        )
        bm25_results = self.bm25_service.search(
            query=query,
            collection=collection,
        )
        return self._merge(vector_results, bm25_results)

    def _merge(self, vector_results: list[dict], bm25_results: list[dict]) -> list[dict]:
        """Merges and deduplicates vector and BM25 results."""
        seen = set()
        merged = []
        for result in vector_results + bm25_results:
            chunk = result["chunk"]
            if chunk not in seen:
                seen.add(chunk)
                merged.append(result)
        return merged