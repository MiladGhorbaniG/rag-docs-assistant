from __future__ import annotations

from typing import Iterator, Protocol


class LLMProvider(Protocol):
    name: str

    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return the full assistant text."""

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Yield text fragments in order."""
