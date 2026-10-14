from __future__ import annotations

import json
import logging
import tempfile
from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import Settings
from app.llm import build_llm
from app.rag.citations import citation_payload, context_block
from app.rag.corpus import InMemoryCorpus
from app.rag.embeddings import HashingEmbedder
from app.rag.ingest import SUPPORTED, ingest_directory, ingest_path

logger = logging.getLogger("booknook")

SYSTEM_PROMPT = (
    "You are the BookNook reading-room assistant. Answer only from the supplied notes. "
    "Cite the bracket numbers that support the answer. If the notes do not contain the "
    "answer, say you cannot find it on the shelf."
)


class ChatIn(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None


def build_corpus(settings: Settings):
    embedder = HashingEmbedder(settings.embedding_dim)
    if settings.database_url:
        from app.db.store import PgCorpus

        corpus = PgCorpus(settings.database_url, embedder, settings.embedding_dim)
        corpus.ensure_schema()
    else:
        corpus = InMemoryCorpus(embedder)
    sample_dir = Path(settings.sample_data_dir)
    if sample_dir.exists() and not corpus.document_ids():
        loaded = ingest_directory(corpus, sample_dir)
        logger.info("loaded %s sample documents", len(loaded))
    return corpus


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = Settings.from_env()
        app.state.settings = settings
        app.state.llm = build_llm(settings)
        app.state.corpus = build_corpus(settings)
        yield

    app = FastAPI(title="BookNook docs assistant", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "llm": app.state.llm.name}

    @app.get("/documents")
    def documents() -> dict:
        return {"documents": app.state.corpus.list_documents()}

    @app.post("/documents")
    async def upload(file: UploadFile = File(...)) -> dict:
        name = Path(file.filename or "upload.md").name
        if Path(name).suffix.lower() not in SUPPORTED:
            raise HTTPException(status_code=400, detail="only markdown and pdf are accepted")
        payload = await file.read()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / name
            path.write_bytes(payload)
            document_id = ingest_path(app.state.corpus, path)
        return {"document_id": document_id}

    @app.post("/chat")
    def chat(body: ChatIn) -> StreamingResponse:
        message = body.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="message is empty")
        scored = app.state.corpus.search(message, app.state.settings.top_k)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {message}\n\nNotes:\n{context_block(scored)}",
            },
        ]
        citations = citation_payload(scored)

        def events() -> Iterator[str]:
            for token in app.state.llm.stream(messages):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'citations': citations})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return app


app = create_app()
