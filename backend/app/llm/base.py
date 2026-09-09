from __future__ import annotations

from typing import Protocol


class LLMProviderError(Exception):
    """Raised when a model provider cannot return a usable response."""


class LLMProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        ...
