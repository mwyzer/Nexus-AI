# Prompt: RAG Implementation

Use this prompt when implementing RAG pipeline features.

---

## Instructions

### RAG Pipeline Flow

```
Document Upload → Parse → Chunk → Embed → Store (pgvector)
                                                      ↓
User Query → Embed Query → Vector Search → Retrieve → Generate Answer
```

### Key Components

#### 1. Document Parser
```python
class DocumentParser:
    async def parse(self, filepath: str, mime_type: str) -> ParsedDocument:
        """Parse document into clean text with metadata."""
        parsers = {
            "application/pdf": self.parse_pdf,
            "text/markdown": self.parse_markdown,
            "text/plain": self.parse_text,
            "text/html": self.parse_html,
        }
        parser = parsers.get(mime_type)
        if not parser:
            raise UnsupportedFormatError(f"Unsupported format: {mime_type}")
        return await parser(filepath)
```

#### 2. Chunker
```python
class Chunker(ABC):
    @abstractmethod
    def split(self, text: str) -> list[Chunk]:
        """Split text into chunks with metadata."""
        pass

# Implementations: FixedSizeChunker, RecursiveChunker, SemanticChunker, MarkdownHeaderChunker
```

#### 3. Embedder
```python
class Embedder(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        pass

# Implementations: OpenAIEmbedder, OllamaEmbedder, VLLMEmbedder
```

#### 4. Vector Store
```python
class VectorStore:
    async def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: ...
    async def search(self, query_embedding: list[float], top_k: int, filters: dict) -> list[SearchResult]: ...
    async def delete(self, document_id: UUID) -> None: ...
```

### Search Implementation
- **Semantic**: ` ORDER BY embedding <=> query_embedding LIMIT k`
- **Keyword**: `ts_rank(to_tsvector('english', content), plainto_tsquery('english', query))`
- **Hybrid**: `score = 0.7 * semantic_score + 0.3 * keyword_score`

### Key Rules
- Validate all file uploads (type, size, content)
- Use async processing via Celery for ingestion
- Store document processing status (pending → processing → ready → error)
- Always include source citations in answers
- Never fabricate information not in context
- Handle empty search results gracefully
- Use connection pooling for database operations
