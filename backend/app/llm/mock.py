from __future__ import annotations

from collections.abc import Iterator


class MockLLM:
    """Deterministic reader used when no API key is configured.

    It quotes the first retrieved note so the demo still cites a real passage.
    """

    name = "mock"

    def complete(self, messages: list[dict[str, str]]) -> str:
        return "".join(self.stream(messages)).strip()

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        user = messages[-1]["content"] if messages else ""
        cited = ""
        snippet = ""
        for line in user.splitlines():
            if line.startswith("[1]"):
                cited = line.strip()
                continue
            if cited and line.strip() and not line.startswith("["):
                snippet = line.strip()
                break
        if cited:
            text = f"From the shelf notes, {cited}. {snippet}"
        else:
            text = "I could not find a BookNook note for that question."
        for part in text.split(" "):
            if part:
                yield part + " "
