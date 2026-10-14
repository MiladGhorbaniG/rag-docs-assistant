from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "where",
    "when",
    "who",
    "why",
    "how",
    "do",
    "does",
    "did",
    "of",
    "to",
    "in",
    "on",
    "for",
    "and",
    "or",
    "at",
    "by",
    "from",
    "with",
    "about",
    "this",
    "that",
    "it",
    "be",
}


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one unit vector per text."""


class HashingEmbedder:
    """Offline bag-of-tokens embedder.

    Feature hashing keeps `docker compose up` and the test suite free of model
    downloads and API keys. Swap in another Embedder when you want a neural model.
    """

    def __init__(self, dim: int = 64) -> None:
        if dim <= 0:
            raise ValueError("embedding dimension must be positive")
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        tokens = [token for token in TOKEN.findall(text.lower()) if token not in STOPWORDS]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
