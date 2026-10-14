import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.llm import build_llm
from app.llm.mock import MockLLM
from app.main import create_app


def test_mock_llm_quotes_first_note() -> None:
    llm = MockLLM()
    text = llm.complete(
        [
            {"role": "system", "content": "cite"},
            {
                "role": "user",
                "content": "Question: hours\n\nNotes:\n[1] Membership — Hours\nOpen Tuesday.",
            },
        ]
    )
    assert "[1]" in text
    assert "Open Tuesday." in text


def test_mock_llm_without_notes() -> None:
    text = MockLLM().complete([{"role": "user", "content": "Question: nothing"}])
    assert "could not find" in text


def test_openai_provider_requires_a_key() -> None:
    with pytest.raises(RuntimeError):
        build_llm(Settings(llm_provider="openai", openai_api_key=""))


def test_unknown_provider() -> None:
    with pytest.raises(RuntimeError):
        build_llm(Settings(llm_provider="somewhere-else"))


def test_health_and_chat_stream() -> None:
    with TestClient(create_app()) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["llm"] == "mock"
        shelf = client.get("/documents")
        assert any(item["id"] == "membership" for item in shelf.json()["documents"])
        response = client.post("/chat", json={"message": "Where do mystery novels stay?"})
        assert response.status_code == 200
        body = response.text
        assert "data:" in body
        assert "[DONE]" in body
        assert "aisle" in body.lower()


def test_upload_markdown_and_reject_plain_text() -> None:
    with TestClient(create_app()) as client:
        rejected = client.post(
            "/documents",
            files={"file": ("notes.txt", b"hello", "text/plain")},
        )
        assert rejected.status_code == 400
        accepted = client.post(
            "/documents",
            files={
                "file": (
                    "tea-shelf.md",
                    b"# Tea shelf\n\n## Kettle\nThe copper kettle lives behind the counter.\n",
                    "text/markdown",
                )
            },
        )
        assert accepted.status_code == 200
        assert accepted.json()["document_id"] == "tea-shelf"
        answer = client.post("/chat", json={"message": "Where does the copper kettle live?"})
        assert "copper kettle" in answer.text.lower()
