from __future__ import annotations

from pathlib import Path

from app.rag.chunking import chunk_document, stable_id
from app.rag.types import Chunk

SUPPORTED = {".md", ".pdf"}


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def read_pdf(path: Path) -> list[tuple[int, str]]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append((index, page.extract_text() or ""))
    return pages


def chunks_for_path(path: Path) -> tuple[str, str, list[Chunk]]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"unsupported file type: {path.name}")
    document_id = path.stem
    if suffix == ".md":
        text = path.read_text(encoding="utf-8")
        title = title_from_markdown(text, document_id)
        return document_id, title, chunk_document(text, document_id=document_id, title=title)

    title = document_id.replace("-", " ")
    chunks: list[Chunk] = []
    ordinal = 0
    for page, text in read_pdf(path):
        for chunk in chunk_document(
            text,
            document_id=document_id,
            title=title,
            page=page,
            ordinal_start=ordinal,
        ):
            chunks.append(
                Chunk(
                    chunk_id=stable_id(document_id, str(ordinal), str(page)),
                    document_id=chunk.document_id,
                    title=chunk.title,
                    heading=chunk.heading,
                    page=page,
                    text=chunk.text,
                    ordinal=ordinal,
                )
            )
            ordinal += 1
    return document_id, title, chunks


def ingest_path(corpus, path: Path) -> str:
    document_id, title, chunks = chunks_for_path(path)
    corpus.add_document(document_id, title, chunks)
    return document_id


def ingest_directory(corpus, directory: Path) -> list[str]:
    loaded: list[str] = []
    if not directory.exists():
        return loaded
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            loaded.append(ingest_path(corpus, path))
    return loaded
