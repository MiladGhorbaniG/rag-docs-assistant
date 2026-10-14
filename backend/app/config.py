from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def default_sample_dir() -> str:
    return str(Path(__file__).resolve().parents[2] / "sample_data")


@dataclass(frozen=True)
class Settings:
    database_url: str = ""
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    embedding_dim: int = 64
    sample_data_dir: str = ""
    top_k: int = 4

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_url=os.environ.get("DATABASE_URL", ""),
            llm_provider=os.environ.get("LLM_PROVIDER", "mock"),
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openai_base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            embedding_dim=int(os.environ.get("EMBEDDING_DIM", "64")),
            sample_data_dir=os.environ.get("SAMPLE_DATA_DIR", "") or default_sample_dir(),
            top_k=int(os.environ.get("TOP_K", "4")),
        )
