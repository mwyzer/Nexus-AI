from abc import ABC, abstractmethod

import httpx
from langchain_openai import OpenAIEmbeddings

from ..config import settings


class Embedder(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""


class OpenAIEmbedder(Embedder):
    def __init__(self, model: str = "text-embedding-3-small"):
        self._client = OpenAIEmbeddings(model=model, api_key=settings.openai_api_key)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._client.aembed_documents(texts)


class OllamaEmbedder(Embedder):
    def __init__(self, model: str = "bge-m3", base_url: str | None = None):
        self.model = model
        self.base_url = base_url or settings.ollama_url

    async def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            for text in texts:
                response = await client.post(
                    "/api/embeddings", json={"model": self.model, "prompt": text}
                )
                response.raise_for_status()
                embeddings.append(response.json()["embedding"])
        return embeddings


def get_embedder(provider: str, model: str) -> Embedder:
    if provider == "openai":
        return OpenAIEmbedder(model=model)
    if provider == "ollama":
        return OllamaEmbedder(model=model)
    raise ValueError(f"Unknown embedding provider: {provider}")
