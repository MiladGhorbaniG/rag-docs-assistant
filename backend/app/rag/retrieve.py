from __future__ import annotations

from app.rag.embeddings import Embedder
from app.rag.types import Chunk, ScoredChunk


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def rank_chunks(
    query: str,
    rows: list[tuple[Chunk, list[float]]],
    embedder: Embedder,
    k: int,
) -> list[ScoredChunk]:
    if k <= 0 or not rows:
        return []
    query_vector = embedder.embed([query])[0]
    scored = [
        ScoredChunk(chunk=chunk, score=cosine(query_vector, vector)) for chunk, vector in rows
    ]
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:k]
