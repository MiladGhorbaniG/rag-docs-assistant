import pytest

from app.rag.chunking import chunk_document, split_sections, windows


def test_headings_become_sections() -> None:
    text = "# Title\n\nIntro line.\n\n## Hours\nOpen Tuesday.\n\n## Fees\nOne credit.\n"
    sections = split_sections(text)
    headings = [heading for heading, _ in sections]
    assert "Title" in headings
    assert "Hours" in headings
    assert "Fees" in headings


def test_windows_overlap() -> None:
    text = "abcdefghijklmnopqrstuvwxyz"
    pieces = windows(text, size=10, overlap=4)
    assert pieces[0] == "abcdefghij"
    assert pieces[1].startswith("ghij")
    assert pieces[-1].endswith("z")


def test_chunk_ids_are_stable() -> None:
    first = chunk_document("Hello shelf.", document_id="note", title="Note")
    second = chunk_document("Hello shelf.", document_id="note", title="Note")
    assert first[0].chunk_id == second[0].chunk_id
    assert first[0].heading == ""


def test_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        windows("abc", size=0, overlap=0)
