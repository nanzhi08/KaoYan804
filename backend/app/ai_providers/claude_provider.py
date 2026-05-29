from anthropic import AsyncAnthropic
from typing import AsyncIterator

from .base import BaseAIProvider
from ..config import settings


class ClaudeProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-6"

    def _convert_messages(self, messages: list[dict]) -> tuple[str | None, list[dict]]:
        system_message = None
        converted = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted.append({"role": msg["role"], "content": msg["content"]})
        return system_message, converted

    async def chat(self, messages: list[dict], **kwargs) -> str:
        system_msg, msgs = self._convert_messages(messages)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_msg or "",
            messages=msgs,
            **kwargs,
        )
        content = response.content[0]
        return content.text if hasattr(content, 'text') else str(content)

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        system_msg, msgs = self._convert_messages(messages)
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=system_msg or "",
            messages=msgs,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text
