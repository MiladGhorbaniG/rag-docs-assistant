from __future__ import annotations

from typing import Protocol

from app.rag.embeddings import Embedder
from app.rag.retrieve import rank_chunks
from app.rag.types import Chunk, ScoredChunk


class Corpus(Protocol):
    def add_document(self, document_id: str, title: str, chunks: list[Chunk]) -> None:
        """Replace any previous chunks for this document."""

    def document_ids(self) -> set[str]:
        """Identifiers currently stored."""

    def list_documents(self) -> list[dict]:
        """Shelf summary used by the chat UI."""

    def search(self, query: str, k: int) -> list[ScoredChunk]:
        """Nearest chunks for a question."""


class InMemoryCorpus:
    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder
        self._rows: list[tuple[Chunk, list[float]]] = []

    def add_document(self, document_id: str, title: str, chunks: list[Chunk]) -> None:
        del title
        self._rows = [row for row in self._rows if row[0].document_id != document_id]
        if not chunks:
            return
        vectors = self.embedder.embed([chunk.text for chunk in chunks])
        self._rows.extend(zip(chunks, vectors))

    def document_ids(self) -> set[str]:
        return {chunk.document_id for chunk, _ in self._rows}

    def list_documents(self) -> list[dict]:
        found: dict[str, str] = {}
        for chunk, _ in self._rows:
            found.setdefault(chunk.document_id, chunk.title)
        return [{"id": doc_id, "title": title} for doc_id, title in sorted(found.items())]

    def search(self, query: str, k: int) -> list[ScoredChunk]:
        return rank_chunks(query, self._rows, self.embedder, k)
