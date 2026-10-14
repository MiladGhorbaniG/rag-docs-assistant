from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings
from app.rag.corpus import InMemoryCorpus
from app.rag.embeddings import HashingEmbedder
from app.rag.ingest import ingest_directory


def hit_rate(corpus, cases: list[dict], k: int) -> dict:
    details = []
    hits = 0
    for case in cases:
        found = corpus.search(case["question"], k)
        ranked = [item.chunk.document_id for item in found]
        ok = case["document_id"] in ranked
        hits += int(ok)
        details.append({"id": case["id"], "hit": ok, "ranked": ranked})
    total = len(cases)
    return {
        "hit_rate": (hits / total) if total else 0.0,
        "hits": hits,
        "total": total,
        "details": details,
    }


def load_cases(sample_dir: Path) -> list[dict]:
    return json.loads((sample_dir / "eval" / "qa.json").read_text(encoding="utf-8"))


def evaluate(settings: Settings | None = None) -> dict:
    settings = settings or Settings.from_env()
    sample_dir = Path(settings.sample_data_dir)
    corpus = InMemoryCorpus(HashingEmbedder(settings.embedding_dim))
    ingest_directory(corpus, sample_dir)
    return hit_rate(corpus, load_cases(sample_dir), settings.top_k)


def main() -> None:
    report = evaluate()
    printable = {key: report[key] for key in ("hit_rate", "hits", "total", "details")}
    print(json.dumps(printable, indent=2))
    if report["hit_rate"] < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
