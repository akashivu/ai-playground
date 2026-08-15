

from __future__ import annotations

import re

from ingestion.models import KnowledgeChunk, KnowledgeDocument


_DELIMITER_RE = re.compile(r"^\s*-{3,}\s*$", re.MULTILINE)


_HEADING_RE = re.compile(r"^(?=.{2,60}$)[A-Z][A-Z0-9 &/'\-]+$")


_QUESTION_RE = re.compile(r"^\s*Question\s*:\s*", re.IGNORECASE | re.MULTILINE)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "section"


def split_faq(document: KnowledgeDocument) -> list[KnowledgeChunk]:
    """
    Split a Q&A-style document into one chunk per Question/Answer pair.

    Input shape:
        Question:
        How do I book a ride?
        Answer:
        ...
        Question:
        Can I travel with pets?
        Answer:
        ...
    """
    content = document.content

    # Drop everything before the first "Question:" (e.g. a "BOOKING FAQ" title line)
    first_match = _QUESTION_RE.search(content)
    if not first_match:
       
        return split_generic(document)

    body = content[first_match.start():]
   
    pieces = _QUESTION_RE.split(body)
    pieces = [p.strip() for p in pieces if p.strip()]

    chunks: list[KnowledgeChunk] = []
    for i, piece in enumerate(pieces):
       
        lines = piece.splitlines()
        question_text = lines[0].strip()
        rest = "\n".join(lines[1:]).strip()

        chunk_text = f"Question: {question_text}\n{rest}"
        chunks.append(
            KnowledgeChunk(
                text=chunk_text,
                source=str(document.source),
                collection=document.collection,
                category=document.category,
                title=question_text,
                chunk_index=i,
                document_id=document.document_id,
                topic=_slugify(question_text),
            )
        )
    return chunks


def split_sections(document: KnowledgeDocument) -> list[KnowledgeChunk]:
    
    content = document.content

    if _DELIMITER_RE.search(content):
        raw_sections = _DELIMITER_RE.split(content)
    else:
        raw_sections = _split_on_headings(content)

    chunks: list[KnowledgeChunk] = []
    idx = 0
    for raw in raw_sections:
        raw = raw.strip()
        if not raw:
            continue
        lines = raw.splitlines()
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        title = heading if heading else document.title

        chunks.append(
            KnowledgeChunk(
                text=raw,
                source=str(document.source),
                collection=document.collection,
                category=document.category,
                title=title,
                chunk_index=idx,
                document_id=document.document_id,
                topic=_slugify(title),
                metadata={"body_only": body} if body else {},
            )
        )
        idx += 1

    return chunks


def _split_on_headings(content: str) -> list[str]:
    """Split on lines that look like ALL-CAPS section headings."""
    lines = content.splitlines()
    sections: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if _HEADING_RE.match(line.strip()) and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)

    if len(sections) <= 1:
        # No internal headings found at all -> whole doc is one section
        return [content]

    return ["\n".join(s) for s in sections]


def split_generic(document: KnowledgeDocument) -> list[KnowledgeChunk]:
    """Fallback: treat the whole document as a single chunk."""
    return [
        KnowledgeChunk(
            text=document.content,
            source=str(document.source),
            collection=document.collection,
            category=document.category,
            title=document.title,
            chunk_index=0,
            document_id=document.document_id,
            topic=_slugify(document.title),
        )
    ]


def split_document(document: KnowledgeDocument) -> list[KnowledgeChunk]:
    """Dispatch to the right splitter based on document category."""
    if document.category == "faq":
        return split_faq(document)
    if document.category in {"policy", "pricing", "vehicle", "city"}:
        return split_sections(document)
    return split_generic(document)
