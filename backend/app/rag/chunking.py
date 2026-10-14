from __future__ import annotations

import re
from hashlib import sha1

from app.rag.types import Chunk

HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)


def stable_id(*parts: str) -> str:
    return sha1("::".join(parts).encode("utf-8")).hexdigest()[:16]


def split_sections(text: str) -> list[tuple[str, str]]:
    matches = list(HEADING.finditer(text))
    if not matches:
        body = text.strip()
        return [("", body)] if body else []

    sections: list[tuple[str, str]] = []
    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections.append(("", preamble))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            sections.append((match.group(2).strip(), body))
    return sections


def windows(text: str, size: int, overlap: int) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    if size <= 0:
        raise ValueError("chunk size must be positive")
    if len(cleaned) <= size:
        return [cleaned]
    step = max(1, size - max(0, overlap))
    pieces: list[str] = []
    start = 0
    while start < len(cleaned):
        piece = cleaned[start : start + size].strip()
        if piece:
            pieces.append(piece)
        if start + size >= len(cleaned):
            break
        start += step
    return pieces


def chunk_document(
    text: str,
    *,
    document_id: str,
    title: str,
    size: int = 480,
    overlap: int = 80,
    page: int | None = None,
    ordinal_start: int = 0,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    ordinal = ordinal_start
    for heading, body in split_sections(text):
        for piece in windows(body, size, overlap):
            chunks.append(
                Chunk(
                    chunk_id=stable_id(document_id, str(ordinal), str(page or 0)),
                    document_id=document_id,
                    title=title,
                    heading=heading,
                    page=page,
                    text=piece,
                    ordinal=ordinal,
                )
            )
            ordinal += 1
    return chunks
