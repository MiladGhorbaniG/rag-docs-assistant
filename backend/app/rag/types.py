from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    heading: str
    page: int | None
    text: str
    ordinal: int


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    score: float
