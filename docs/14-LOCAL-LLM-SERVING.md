# 14 — Local LLM Serving Specification

## Overview

Nexus AI supports serving LLMs locally for organizations with data sovereignty requirements, air-gapped environments, or cost optimization needs.

## Supported Serving Engines

| Engine              | Use Case                        |
|---------------------|---------------------------------|
| Ollama              | Quick setup, single-node dev    |
| vLLM                | Production, high throughput     |
| llama.cpp           | CPU-only, resource-constrained  |
| Text Generation Inference (TGI) | HuggingFace native   |

## Architecture

```
┌──────────────────────────────────────────────┐
│              Nexus AI Platform                │
│                                               │
│  ┌──────────┐        ┌────────────────────┐  │
│  │ AI       │───────→│ LLM Provider        │  │
│  │ Backend  │        │ (Abstraction Layer)  │  │
│  └──────────┘        └─────────┬──────────┘  │
│                                │              │
│              ┌─────────────────┼──────────┐   │
│              │                 │          │   │
│        ┌─────▼────┐   ┌───────▼────┐ ┌───▼───▼┐ │
│        │  OpenAI   │   │  Ollama    │ │ vLLM  │ │
│        │  (cloud)  │   │  (local)   │ │(local)│ │
│        └──────────┘   └────────────┘ └───────┘ │
└──────────────────────────────────────────────┘
```

## LLM Provider Abstraction

```python
# ai-backend/app/llm/provider.py
from abc import ABC, abstractmethod
from typing import AsyncIterator

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str: ...
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]: ...
    
    @abstractmethod
    async def embed(self, texts: list[str], model: str) -> list[list[float]]: ...

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

class VLLMProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:8000/v1"):
        self.client = AsyncOpenAI(
            api_key="not-needed",
            base_url=base_url,
        )
```

## Provider Configuration

```python
class LLMConfig(BaseModel):
    provider: Literal["openai", "ollama", "vllm", "tgi"] = "openai"
    model: str = "gpt-4o"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Local provider settings
    max_concurrent: int = 4
    timeout: int = 120
    
    # Fallback chain
    fallback_providers: list[str] = []

class LLMProviderFactory:
    @staticmethod
    def create(config: LLMConfig) -> LLMProvider:
        providers = {
            "openai": lambda: OpenAIProvider(config.api_key, config.base_url),
            "ollama": lambda: OllamaProvider(config.base_url or "http://localhost:11434"),
            "vllm": lambda: VLLMProvider(config.base_url or "http://localhost:8000/v1"),
            "tgi": lambda: TGIProvider(config.base_url),
        }
        return providers[config.provider]()
```

## Multi-Provider with Fallback

```python
class MultiProviderLLM(LLMProvider):
    def __init__(self, providers: list[tuple[str, LLMProvider]]):
        self.providers = providers  # [(name, provider), ...]
    
    async def generate(self, prompt: str, **kwargs) -> str:
        for name, provider in self.providers:
            try:
                return await provider.generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {name} failed: {e}")
                continue
        raise AllProvidersFailedError("All LLM providers failed")
```

## Ollama Docker Compose

```yaml
# infrastructure/docker-compose.ollama.yml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_HOST=0.0.0.0

  ollama-init:
    image: ollama/ollama:latest
    depends_on:
      - ollama
    entrypoint: /bin/sh
    command:
      - -c
      - |
        sleep 5
        ollama pull llama3.1:8b
        ollama pull nomic-embed-text
    environment:
      - OLLAMA_HOST=ollama:11434

volumes:
  ollama_data:
```

## Model Management

```python
# List available local models
@router.get("/llm/models")
async def list_local_models(provider: str = "ollama"):
    if provider == "ollama":
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            return resp.json()
    elif provider == "vllm":
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{VLLM_URL}/v1/models")
            return resp.json()
```

## Recommended Local Models

| Task            | Model              | Size  | RAM Required |
|-----------------|--------------------|-------|--------------|
| Chat/Agent      | Llama 3.1 8B       | 4.7GB | 8GB          |
| Chat/Agent      | Llama 3.1 70B      | 40GB  | 48GB         |
| Embedding       | nomic-embed-text   | 274MB | 1GB          |
| Embedding       | mxbai-embed-large  | 669MB | 2GB          |
| Code            | DeepSeek Coder V2  | 8.9GB | 16GB         |
