from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, create_engine, delete, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.rag.embeddings import Embedder
from app.rag.types import Chunk, ScoredChunk


def build_models(dim: int):
    class Base(DeclarativeBase):
        pass

    class DocumentRow(Base):
        __tablename__ = "documents"

        id: Mapped[str] = mapped_column(String(64), primary_key=True)
        title: Mapped[str] = mapped_column(String(240))
        source_name: Mapped[str] = mapped_column(String(240))

    class ChunkRow(Base):
        __tablename__ = "chunks"

        id: Mapped[str] = mapped_column(String(64), primary_key=True)
        document_id: Mapped[str] = mapped_column(
            ForeignKey("documents.id", ondelete="CASCADE"),
            index=True,
        )
        ordinal: Mapped[int] = mapped_column(Integer)
        heading: Mapped[str] = mapped_column(String(240), default="")
        page: Mapped[int | None] = mapped_column(Integer, nullable=True)
        text: Mapped[str] = mapped_column(Text)
        embedding: Mapped[list[float]] = mapped_column(Vector(dim))

    return Base, DocumentRow, ChunkRow


class PgCorpus:
    """Postgres + pgvector shelf. Same methods as the in-memory corpus."""

    def __init__(self, database_url: str, embedder: Embedder, dim: int) -> None:
        self.embedder = embedder
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Base, self.DocumentRow, self.ChunkRow = build_models(dim)
        self.Session = sessionmaker(bind=self.engine)

    def ensure_schema(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        self.Base.metadata.create_all(self.engine)

    def add_document(self, document_id: str, title: str, chunks: list[Chunk]) -> None:
        vectors = self.embedder.embed([chunk.text for chunk in chunks]) if chunks else []
        with self.Session() as session:
            existing = session.get(self.DocumentRow, document_id)
            if existing is not None:
                session.execute(
                    delete(self.ChunkRow).where(self.ChunkRow.document_id == document_id)
                )
                session.delete(existing)
                session.flush()
            session.add(self.DocumentRow(id=document_id, title=title, source_name=title))
            for chunk, vector in zip(chunks, vectors):
                session.add(
                    self.ChunkRow(
                        id=chunk.chunk_id,
                        document_id=document_id,
                        ordinal=chunk.ordinal,
                        heading=chunk.heading,
                        page=chunk.page,
                        text=chunk.text,
                        embedding=vector,
                    )
                )
            session.commit()

    def document_ids(self) -> set[str]:
        with self.Session() as session:
            rows = session.scalars(select(self.DocumentRow.id)).all()
        return set(rows)

    def list_documents(self) -> list[dict]:
        with self.Session() as session:
            rows = session.scalars(select(self.DocumentRow).order_by(self.DocumentRow.title)).all()
        return [{"id": row.id, "title": row.title} for row in rows]

    def search(self, query: str, k: int) -> list[ScoredChunk]:
        if k <= 0:
            return []
        query_vector = self.embedder.embed([query])[0]
        distance = self.ChunkRow.embedding.cosine_distance(query_vector)
        statement = (
            select(self.ChunkRow, self.DocumentRow.title, distance)
            .join(self.DocumentRow, self.DocumentRow.id == self.ChunkRow.document_id)
            .order_by(distance)
            .limit(k)
        )
        with self.Session() as session:
            rows = session.execute(statement).all()
        scored: list[ScoredChunk] = []
        for chunk_row, title, dist in rows:
            chunk = Chunk(
                chunk_id=chunk_row.id,
                document_id=chunk_row.document_id,
                title=title,
                heading=chunk_row.heading or "",
                page=chunk_row.page,
                text=chunk_row.text,
                ordinal=chunk_row.ordinal,
            )
            scored.append(ScoredChunk(chunk=chunk, score=1.0 - float(dist)))
        return scored
