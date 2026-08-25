from __future__ import annotations

from services.retrieval_service import RetrievalService
from services.bm25_service import BM25Service
from services.reranking_service import RerankingService


class HybridRetrievalService:
    """
    Combines vector search and BM25 retrieval using
    Reciprocal Rank Fusion (RRF), followed by reranking.
    """

    RRF_K = 60

    def __init__(
        self,
        retrieval_service: RetrievalService,
        bm25_service: BM25Service,
        reranking_service: RerankingService,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.bm25_service = bm25_service
        self.reranking_service = reranking_service

    def search(
        self,
        query: str,
        top_k: int = 5,
        collection: str | None = None,
    ) -> list[dict]:
        """
        Retrieves candidate documents using vector + BM25,
        fuses rankings using RRF, then reranks the fused
        candidates.
        """

        candidate_k = max(
            top_k * 3,
            10,
        )

        vector_results = (
            self.retrieval_service.search(
                query=query,
                top_k=candidate_k,
                collection=collection,
            )
        )

        bm25_results = (
            self.bm25_service.search(
                query=query,
                top_k=candidate_k,
                collection=collection,
            )
        )

        rrf_scores: dict[str, float] = {}
        metadata_by_chunk: dict[str, dict] = {}

        # -----------------------------------------------------
        # VECTOR RESULTS
        # -----------------------------------------------------

        for rank, result in enumerate(
            vector_results,
            start=1,
        ):
            chunk = result["chunk"]

            score = (
                1.0
                / (self.RRF_K + rank)
            )

            rrf_scores[chunk] = (
                rrf_scores.get(chunk, 0.0)
                + score
            )

            metadata_by_chunk.setdefault(
                chunk,
                dict(result),
            )

        # -----------------------------------------------------
        # BM25 RESULTS
        # -----------------------------------------------------

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):
            # BM25Service returns structured dictionaries.

            if not isinstance(result, dict):
                continue

            chunk = result.get("chunk")

            if not chunk:
                continue

            score = (
                1.0
                / (self.RRF_K + rank)
            )

            rrf_scores[chunk] = (
                rrf_scores.get(chunk, 0.0)
                + score
            )

            metadata_by_chunk.setdefault(
                chunk,
                dict(result),
            )

        # -----------------------------------------------------
        # RRF ORDERING
        # -----------------------------------------------------

        fused = sorted(
            rrf_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        # -----------------------------------------------------
        # BUILD RERANK CANDIDATES
        # -----------------------------------------------------

        candidates: list[dict] = []

        for chunk, rrf_score in fused:
            result = dict(
                metadata_by_chunk.get(
                    chunk,
                    {},
                )
            )

            result["chunk"] = chunk
            result["rrf_score"] = rrf_score

            candidates.append(result)

        # -----------------------------------------------------
        # RERANK
        # -----------------------------------------------------

        reranked = (
            self.reranking_service.rerank(
                query=query,
                chunks=candidates,
                top_k=top_k,
            )
        )

        # -----------------------------------------------------
        # RESTORE METADATA
        # -----------------------------------------------------

        metadata_lookup = {
            item["chunk"]: item
            for item in candidates
        }

        final_results: list[dict] = []

        for result in reranked:
            chunk = result["chunk"]

            original = metadata_lookup.get(
                chunk,
                {},
            )

            merged = {
                **original,
                **result,
                "chunk": chunk,
            }

            final_results.append(
                merged
            )

        return final_results