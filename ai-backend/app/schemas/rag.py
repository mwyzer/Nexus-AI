from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: UUID
    filename: str
    chunk_index: int
    text_snippet: str
    relevance_score: float


class RAGQuery(BaseModel):
    question: str = Field(min_length=1)
    knowledge_base_id: UUID
    top_k: int = Field(default=5, ge=1, le=20)
    search_type: str = "hybrid"


class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    processing_time_ms: float
