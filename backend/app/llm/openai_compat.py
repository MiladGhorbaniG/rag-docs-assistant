from __future__ import annotations

import json
from collections.abc import Iterator


class OpenAICompatibleLLM:
    """Chat-completions client for any OpenAI-compatible base URL."""

    name = "openai"

    def __init__(self, *, api_key: str, base_url: str, model: str, timeout: float = 60.0) -> None:
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is empty")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def complete(self, messages: list[dict[str, str]]) -> str:
        return "".join(self.stream(messages))

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        import httpx

        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.model, "messages": messages, "stream": True}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if data == "[DONE]":
                        break
                    body = json.loads(data)
                    delta = body["choices"][0].get("delta", {}).get("content") or ""
                    if delta:
                        yield delta
