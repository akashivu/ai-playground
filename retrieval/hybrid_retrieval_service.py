

from __future__ import annotations

import logging

from .bm25_search import BM25Search
from .models import RetrievalResult
from .rrf import ReciprocalRankFusion
from .validator import RetrievalValidator
from .vector_search import VectorSearcher

logger = logging.getLogger(__name__)


class HybridRetrievalService:
    def __init__(
        self,
        vector_searcher: VectorSearcher,
        bm25_searcher: BM25Search,
        fusion: ReciprocalRankFusion | None = None,
        validator: RetrievalValidator | None = None,
        candidate_pool_size: int = 20,
    ):
        self.vector_searcher = vector_searcher
        self.bm25_searcher = bm25_searcher
        self.fusion = fusion or ReciprocalRankFusion()
        self.validator = validator or RetrievalValidator()
        self.candidate_pool_size = candidate_pool_size

    def search(
        self, query: str, category: str | None = None
    ) -> list[RetrievalResult]:
        logger.info("Query: %r (category=%s)", query, category)

        vector_results = self.vector_searcher.search(
            query, top_k=self.candidate_pool_size, category=category
        )
        logger.info(
            "Vector results (%d): %s",
            len(vector_results),
            [f"{r.document_id}#{r.chunk_index}:{r.vector_score:.3f}" for r in vector_results[:5]],
        )

        bm25_results = self.bm25_searcher.search(
            query, top_k=self.candidate_pool_size, category=category
        )
        logger.info(
            "BM25 results (%d): %s",
            len(bm25_results),
            [f"{r.document_id}#{r.chunk_index}:{r.bm25_score:.3f}" for r in bm25_results[:5]],
        )

        fused = self.fusion.fuse(vector_results, bm25_results)
        logger.info(
            "RRF ranking (%d): %s",
            len(fused),
            [f"{r.document_id}#{r.chunk_index}:{r.fusion_score:.4f}" for r in fused[:5]],
        )

        validated = self.validator.validate(fused, category=category)
        if not validated:
            logger.info("No results passed validation for query %r", query)
        else:
            logger.info(
                "Final top-%d: %s",
                len(validated),
                [r.document_id for r in validated],
            )

        return validated
