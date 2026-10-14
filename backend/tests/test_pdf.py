from pathlib import Path

from app.rag.ingest import chunks_for_path, read_pdf


def test_sample_pdf_page_is_readable() -> None:
    path = Path(__file__).resolve().parents[2] / "sample_data" / "rainy-day-shelf.pdf"
    pages = read_pdf(path)
    assert pages[0][0] == 1
    assert "blue bin" in pages[0][1]


def test_pdf_chunks_keep_page_number() -> None:
    path = Path(__file__).resolve().parents[2] / "sample_data" / "rainy-day-shelf.pdf"
    document_id, title, chunks = chunks_for_path(path)
    assert document_id == "rainy-day-shelf"
    assert "rainy day shelf" in title
    assert chunks[0].page == 1
    assert "garden door" in chunks[0].text
