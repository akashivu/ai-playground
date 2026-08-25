from __future__ import annotations

import re
import unicodedata


class RerankingService:
    """
    Deterministic production reranker for retrieved knowledge chunks.

    Design goals:
    - Preserve all existing result metadata.
    - Combine RRF retrieval quality with lexical relevance.
    - Handle common domain morphology.
    - Ignore conversational stop words.
    - Reward exact phrase matches.
    - Reward query-term coverage.
    - Provide deterministic ordering.
    - Keep the existing `score` field untouched.
    - Expose `rerank_score` separately.
    """

    STOP_WORDS = frozenset(
        {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "can",
            "could",
            "do",
            "does",
            "for",
            "from",
            "how",
            "i",
            "is",
            "me",
            "of",
            "on",
            "or",
            "please",
            "tell",
            "the",
            "to",
            "what",
            "when",
            "where",
            "which",
            "with",
            "would",
            "you",
            "your",
        }
    )

    TERM_NORMALIZATION = {
        "cancel": "cancel",
        "canceled": "cancel",
        "cancelled": "cancel",
        "canceling": "cancel",
        "cancelling": "cancel",
        "cancellation": "cancel",
        "cancellations": "cancel",
        "refund": "refund",
        "refunds": "refund",
        "refunded": "refund",
        "refunding": "refund",
        "policy": "policy",
        "policies": "policy",
        "book": "book",
        "booking": "book",
        "bookings": "book",
        "booked": "book",
        "itinerary": "itinerary",
        "itineraries": "itinerary",
        "service": "service",
        "services": "service",
    }

    RRF_WEIGHT = 0.40
    LEXICAL_WEIGHT = 0.45
    PHRASE_WEIGHT = 0.15

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        normalized = unicodedata.normalize(
            "NFKC",
            text or "",
        )

        normalized = normalized.lower()

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

        return normalized

    @classmethod
    def _normalize_token(cls, token: str) -> str:
        token = token.strip().lower()

        if not token:
            return ""

        return cls.TERM_NORMALIZATION.get(
            token,
            token,
        )

    @classmethod
    def _tokenize(cls, text: str) -> list[str]:
        normalized = cls._normalize_text(text)

        raw_tokens = re.findall(
            r"[a-z0-9]+",
            normalized,
        )

        tokens: list[str] = []

        for token in raw_tokens:
            if token in cls.STOP_WORDS:
                continue

            normalized_token = cls._normalize_token(
                token
            )

            if normalized_token:
                tokens.append(normalized_token)

        return tokens

    @classmethod
    def _unique_tokens(
        cls,
        text: str,
    ) -> set[str]:
        return set(
            cls._tokenize(text)
        )

    @classmethod
    def _normalized_phrase(
        cls,
        text: str,
    ) -> str:
        return " ".join(
            cls._tokenize(text)
        )

    @classmethod
    def _phrase_score(
        cls,
        query: str,
        chunk_text: str,
    ) -> float:
        query_phrase = cls._normalized_phrase(
            query
        )

        chunk_phrase = cls._normalized_phrase(
            chunk_text
        )

        if not query_phrase:
            return 0.0

        if query_phrase in chunk_phrase:
            return 1.0

        query_tokens = query_phrase.split()
        chunk_tokens = chunk_phrase.split()

        if len(query_tokens) < 2:
            return 0.0

        matching_adjacent_pairs = 0
        total_pairs = len(query_tokens) - 1

        for index in range(total_pairs):
            pair = (
                query_tokens[index],
                query_tokens[index + 1],
            )

            for chunk_index in range(
                len(chunk_tokens) - 1
            ):
                chunk_pair = (
                    chunk_tokens[chunk_index],
                    chunk_tokens[chunk_index + 1],
                )

                if chunk_pair == pair:
                    matching_adjacent_pairs += 1
                    break

        if total_pairs == 0:
            return 0.0

        return (
            matching_adjacent_pairs
            / total_pairs
        )

    @classmethod
    def _lexical_score(
        cls,
        query: str,
        chunk_text: str,
    ) -> float:
        query_tokens = cls._unique_tokens(
            query
        )

        chunk_tokens = cls._unique_tokens(
            chunk_text
        )

        if not query_tokens or not chunk_tokens:
            return 0.0

        overlap = query_tokens.intersection(
            chunk_tokens
        )

        if not overlap:
            return 0.0

        query_coverage = (
            len(overlap)
            / len(query_tokens)
        )

        chunk_precision = (
            len(overlap)
            / max(
                len(chunk_tokens),
                1,
            )
        )

        base_score = (
            0.75 * query_coverage
            + 0.25 * min(
                chunk_precision * 5.0,
                1.0,
            )
        )

        return min(
            base_score,
            1.0,
        )

    @staticmethod
    def _normalize_rrf_scores(
        chunks: list[dict],
    ) -> dict[int, float]:
        values = [
            float(
                item.get(
                    "rrf_score",
                    0.0,
                )
            )
            for item in chunks
        ]

        if not values:
            return {}

        minimum = min(values)
        maximum = max(values)

        if maximum <= minimum:
            return {
                index: 1.0
                for index in range(
                    len(chunks)
                )
            }

        scale = maximum - minimum

        return {
            index: (
                (
                    float(
                        item.get(
                            "rrf_score",
                            0.0,
                        )
                    )
                    - minimum
                )
                / scale
            )
            for index, item in enumerate(
                chunks
            )
        }

    @classmethod
    def _score_candidate(
        cls,
        query: str,
        chunk: dict,
        normalized_rrf: float,
    ) -> float:
        chunk_text = str(
            chunk.get(
                "chunk",
                "",
            )
        )

        lexical_score = cls._lexical_score(
            query,
            chunk_text,
        )

        phrase_score = cls._phrase_score(
            query,
            chunk_text,
        )

        final_score = (
            cls.RRF_WEIGHT * normalized_rrf
            + cls.LEXICAL_WEIGHT * lexical_score
            + cls.PHRASE_WEIGHT * phrase_score
        )

        return round(
            max(
                0.0,
                min(
                    final_score,
                    1.0,
                ),
            ),
            6,
        )

    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Rerank retrieved candidates while preserving all metadata.
        """

        if not query or not query.strip():
            return chunks[:top_k]

        if not chunks:
            return []

        safe_top_k = max(
            int(top_k),
            1,
        )

        normalized_rrf = (
            self._normalize_rrf_scores(
                chunks
            )
        )

        scored: list[tuple[int, dict]] = []

        for index, chunk in enumerate(
            chunks
        ):
            if not isinstance(
                chunk,
                dict,
            ):
                continue

            chunk_text = str(
                chunk.get(
                    "chunk",
                    "",
                )
            ).strip()

            if not chunk_text:
                continue

            retrieval_score = normalized_rrf.get(
                index,
                0.0,
            )

            lexical_score = (
                self._lexical_score(
                    query,
                    chunk_text,
                )
            )

            phrase_score = (
                self._phrase_score(
                    query,
                    chunk_text,
                )
            )

            rerank_score = (
                self._score_candidate(
                    query=query,
                    chunk=chunk,
                    normalized_rrf=retrieval_score,
                )
            )

            result = {
                **chunk,
                "retrieval_score": round(
                    retrieval_score,
                    6,
                ),
                "lexical_score": round(
                    lexical_score,
                    6,
                ),
                "phrase_score": round(
                    phrase_score,
                    6,
                ),
                "rerank_score": rerank_score,
            }

            scored.append(
                (
                    index,
                    result,
                )
            )

        scored.sort(
            key=lambda pair: (
                pair[1]["rerank_score"],
                pair[1].get(
                    "rrf_score",
                    0.0,
                ),
                pair[1].get(
                    "lexical_score",
                    0.0,
                ),
            ),
            reverse=True,
        )

        return [
            result
            for _, result in scored[:safe_top_k]
        ]

    def deduplicate(
        self,
        chunks: list[dict],
    ) -> list[dict]:
        """
        Remove duplicate chunk text while preserving the first occurrence.
        """

        if not chunks:
            return []

        unique_chunks: list[dict] = []
        seen: set[str] = set()

        for chunk in chunks:
            if not isinstance(
                chunk,
                dict,
            ):
                continue

            text = str(
                chunk.get(
                    "chunk",
                    "",
                )
            ).strip()

            if not text:
                continue

            normalized = self._normalize_text(
                text
            )

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_chunks.append(chunk)

        return unique_chunks