from app.rag.citations import citation_payload, context_block
from app.rag.corpus import InMemoryCorpus
from app.rag.embeddings import HashingEmbedder
from app.rag.types import Chunk


def _chunk(document_id: str, text: str, heading: str = "Hours") -> Chunk:
    return Chunk(
        chunk_id=document_id,
        document_id=document_id,
        title="Membership",
        heading=heading,
        page=None,
        text=text,
        ordinal=0,
    )


def test_vectors_are_normalized_and_stable() -> None:
    embedder = HashingEmbedder(dim=32)
    first = embedder.embed(["mystery novels on aisle M"])[0]
    second = embedder.embed(["mystery novels on aisle M"])[0]
    assert first == second
    norm = sum(value * value for value in first) ** 0.5
    assert abs(norm - 1.0) < 1e-9


def test_empty_text_is_zero_vector() -> None:
    vector = HashingEmbedder(dim=8).embed(["??? ..."])[0]
    assert vector == [0.0] * 8


def test_search_prefers_the_matching_note() -> None:
    embedder = HashingEmbedder()
    corpus = InMemoryCorpus(embedder)
    corpus.add_document(
        "membership",
        "Membership",
        [_chunk("membership", "The late fee is one book credit per day after seven days.")],
    )
    corpus.add_document(
        "shelving",
        "Shelving",
        [
            Chunk(
                chunk_id="shelving",
                document_id="shelving",
                title="Shelving",
                heading="Fiction",
                page=2,
                text="Mystery novels stay on aisle M in the rainy day corner.",
                ordinal=0,
            )
        ],
    )
    found = corpus.search("Where do mystery novels stay?", k=1)
    assert found[0].chunk.document_id == "shelving"
    assert found[0].score > 0


def test_citation_block_includes_marker_and_page() -> None:
    embedder = HashingEmbedder()
    corpus = InMemoryCorpus(embedder)
    corpus.add_document(
        "shelving",
        "Shelving",
        [
            Chunk(
                chunk_id="shelving",
                document_id="shelving",
                title="Shelving guide",
                heading="",
                page=3,
                text="Atlases lie flat on the oak table.",
                ordinal=0,
            )
        ],
    )
    scored = corpus.search("atlases oak table", k=1)
    payload = citation_payload(scored)
    assert payload[0]["marker"] == 1
    assert payload[0]["page"] == 3
    block = context_block(scored)
    assert "[1] Shelving guide — p. 3" in block
