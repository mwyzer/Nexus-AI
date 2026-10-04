import httpx
from langchain_openai import ChatOpenAI

from ..config import settings


class LLMCompletionError(Exception):
    """Raised when the configured LLM provider fails to produce a completion."""


async def _complete_openai(prompt: str) -> str:
    llm = ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0.2)
    response = await llm.ainvoke(prompt)
    return str(response.content)


async def _complete_ollama(prompt: str) -> str:
    async with httpx.AsyncClient(base_url=settings.ollama_url, timeout=120.0) as client:
        response = await client.post(
            "/api/generate",
            json={"model": settings.llm_model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"]


async def complete(prompt: str) -> str:
    """Run a single text completion against the configured LLM provider."""
    try:
        if settings.llm_provider == "ollama":
            return await _complete_ollama(prompt)
        return await _complete_openai(prompt)
    except httpx.HTTPError as exc:
        raise LLMCompletionError(f"Ollama request failed: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 - normalize any provider SDK error
        raise LLMCompletionError(f"LLM completion failed: {exc}") from exc
