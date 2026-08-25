from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ChunkConfig(BaseModel):
    strategy: Literal["fixed", "recursive", "semantic", "markdown"] = "recursive"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: list[str] = ["\n\n", "\n", ". ", " "]


class ChunkSchema(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    chunk_metadata: dict[str, Any] = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchQuery(BaseModel):
    query: str = Field(min_length=1)
    knowledge_base_id: UUID
    top_k: int = Field(default=5, ge=1, le=50)
    search_type: Literal["semantic", "keyword", "hybrid"] = "hybrid"
    hybrid_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    content: str
    chunk_index: int
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    search_type: str
