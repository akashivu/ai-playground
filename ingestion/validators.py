

from __future__ import annotations

import logging

from ingestion.models import KnowledgeChunk

logger = logging.getLogger(__name__)

MIN_CHUNK_LENGTH = 20  # characters


def validate_chunks(chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
    seen_text: set[str] = set()
    valid: list[KnowledgeChunk] = []

    for chunk in chunks:
        text = chunk.text.strip()

        if not text:
            logger.warning(
                "Dropping empty chunk: %s (index %d)", chunk.source, chunk.chunk_index
            )
            continue

        if len(text) < MIN_CHUNK_LENGTH:
            logger.warning(
                "Dropping too-short chunk (%d chars) from %s: %r",
                len(text), chunk.source, text,
            )
            continue

        dedup_key = f"{chunk.collection}:{text}"
        if dedup_key in seen_text:
            logger.warning(
                "Dropping duplicate chunk from %s (index %d)",
                chunk.source, chunk.chunk_index,
            )
            continue
        seen_text.add(dedup_key)

        valid.append(chunk)

    return valid
