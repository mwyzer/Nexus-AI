import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base

# Fixed at the BAAI/bge-m3 dimension (the platform default, served via Ollama).
# Embedding models with a different dimension are not yet supported by a single
# knowledge base — see docs/06-AI-RAG-SPECIFICATION.md.
EMBEDDING_DIM = 1024


class ChunkEmbedding(Base):
    """Vector embedding for a chunk, searchable via pgvector."""

    __tablename__ = "chunk_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(
        UUID(as_uuid=True), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False
    )
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)
    model = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<ChunkEmbedding {self.chunk_id}>"
