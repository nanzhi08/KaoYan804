from openai import AsyncOpenAI
from typing import AsyncIterator

from .base import BaseAIProvider
from ..config import settings


class DeepSeekProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
        )
        self.model = "deepseek-chat"

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
