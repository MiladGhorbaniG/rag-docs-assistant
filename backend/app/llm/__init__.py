from __future__ import annotations

from app.config import Settings
from app.llm.base import LLMProvider
from app.llm.mock import MockLLM
from app.llm.openai_compat import OpenAICompatibleLLM


def build_llm(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLM()
    if settings.llm_provider == "openai":
        return OpenAICompatibleLLM(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
        )
    raise RuntimeError(f"unknown LLM_PROVIDER: {settings.llm_provider}")
