from __future__ import annotations

from app.rag.types import ScoredChunk


def citation_payload(scored: list[ScoredChunk], quote_chars: int = 240) -> list[dict]:
    payload = []
    for marker, item in enumerate(scored, start=1):
        chunk = item.chunk
        payload.append(
            {
                "marker": marker,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "heading": chunk.heading,
                "page": chunk.page,
                "quote": chunk.text[:quote_chars],
                "score": round(item.score, 4),
            }
        )
    return payload


def context_block(scored: list[ScoredChunk]) -> str:
    blocks = []
    for item in citation_payload(scored):
        if item["heading"]:
            place = item["heading"]
        elif item["page"]:
            place = f"p. {item['page']}"
        else:
            place = "passage"
        blocks.append(f"[{item['marker']}] {item['title']} — {place}\n{item['quote']}")
    return "\n\n".join(blocks)
