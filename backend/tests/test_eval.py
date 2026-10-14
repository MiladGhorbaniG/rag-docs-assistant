from pathlib import Path

from app.eval.run_eval import evaluate, hit_rate
from app.rag.corpus import InMemoryCorpus
from app.rag.embeddings import HashingEmbedder
from app.rag.ingest import ingest_directory


def test_sample_shelf_hit_rate_is_perfect() -> None:
    report = evaluate()
    assert report["total"] == 4
    assert report["hit_rate"] == 1.0
    assert all(item["hit"] for item in report["details"])


def test_hit_rate_on_empty_cases() -> None:
    corpus = InMemoryCorpus(HashingEmbedder())
    assert hit_rate(corpus, [], k=3)["hit_rate"] == 0.0


def test_ingest_directory_skips_eval_json() -> None:
    sample = Path(__file__).resolve().parents[2] / "sample_data"
    corpus = InMemoryCorpus(HashingEmbedder())
    loaded = ingest_directory(corpus, sample)
    assert "qa" not in loaded
    assert "membership" in loaded
