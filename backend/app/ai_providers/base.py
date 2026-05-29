from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseAIProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        pass

    @abstractmethod
    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        pass
