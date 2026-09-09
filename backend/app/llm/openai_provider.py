from __future__ import annotations

from openai import OpenAI

from app.llm.base import LLMProviderError


class OpenAIProvider:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
        except Exception as error:
            raise LLMProviderError("The configured AI provider is unavailable.") from error

        content = response.choices[0].message.content
        if not content:
            raise LLMProviderError("The AI provider returned an empty response.")
        return content
