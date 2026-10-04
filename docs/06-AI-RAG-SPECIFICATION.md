# 06 — AI RAG Specification

## RAG Pipeline Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Ingest  │ →  │  Chunk   │ →  │  Embed   │ →  │  Store   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
┌──────────┐    ┌──────────┐    ┌──────────┐         │
│ Generate │ ←  │  Re-rank │ ←  │ Retrieve │ ←───────┘
└──────────┘    └──────────┘    └──────────┘
```

## Document Ingestion

### Supported Formats

- PDF (via PyPDF2 / pdfplumber)
- Markdown (.md)
- Plain text (.txt)
- HTML
- CSV / JSON (structured data) — *planned*

### Ingestion Pipeline

```python
# ai-backend/app/rag/ingestion.py
class IngestionPipeline:
    def __init__(self, chunker: Chunker, embedder: Embedder, store: VectorStore):
        self.chunker = chunker
        self.embedder = embedder
        self.store = store
    
    async def ingest(self, document: Document) -> IngestResult:
        # 1. Parse document into text
        # 2. Clean and normalize text
        # 3. Split into chunks
        # 4. Generate embeddings
        # 5. Store in pgvector
        pass
```

## Chunking Strategies

| Strategy         | Description                           | Use Case              |
|------------------|---------------------------------------|-----------------------|
| Fixed Size       | Split by character/token count        | General documents     |
| Recursive        | Split by separators hierarchically    | Code, structured text |
| Semantic         | Split by semantic boundaries          | Long articles         |
| Markdown Header  | Split by heading levels               | Documentation         |

### Chunk Configuration

```python
class ChunkConfig(BaseModel):
    strategy: Literal["fixed", "recursive", "semantic", "markdown"]
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: list[str] = ["\n\n", "\n", ". ", " "]
```

## Embedding Models

| Model                  | Dimensions | Provider |
|------------------------|------------|----------|
| text-embedding-3-small | 1536       | OpenAI   |
| text-embedding-3-large | 3072       | OpenAI   |
| bge-large-en-v1.5      | 1024       | Local    |
| mxbai-embed-large      | 1024       | Local    |

> **Note:** the `chunk_embeddings.embedding` column is currently fixed at `vector(1536)` (see docs/04). Models with non-1536 dimensions (e.g. local 1024-dim) require adapting the vector column to their dimension.

## Vector Store (pgvector)

### Search Types

1. **Semantic Search** — pure vector similarity
2. **Keyword Search** — full-text (PostgreSQL `tsvector`)
3. **Hybrid Search** — combines semantic + keyword with configurable weights
4. **Filtered Search** — metadata-filtered vector search

### Query Interface

```python
class SearchQuery(BaseModel):
    query: str
    knowledge_base_id: UUID
    top_k: int = 5
    search_type: Literal["semantic", "keyword", "hybrid"] = "hybrid"
    filters: dict[str, Any] = {}
    hybrid_weight: float = 0.7  # semantic vs keyword balance
```

## Retrieval Strategies

### Basic Retrieval
- Vector similarity with cosine distance
- Top-k results
- Score threshold filtering

### Advanced Retrieval

1. **Multi-Query Retrieval** — generate multiple query variants
2. **Contextual Compression** — compress retrieved chunks
3. **Re-ranking** — Cross-encoder re-ranking via Cohere/BGE
4. **Recursive Retrieval** — retrieve then retrieve again within results
5. **Time-Decay Weighting** — boost recent documents

## Generation

### Prompt Template

```
You are an AI assistant with access to a knowledge base.
Answer the user's question based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer based on the context provided
- Cite sources using [1], [2] format
- If the context doesn't contain the answer, say so
- Be concise and accurate
```

### Response Format

```python
class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    processing_time_ms: float

class Citation(BaseModel):
    document_id: UUID
    filename: str
    chunk_index: int
    text_snippet: str
    relevance_score: float
```

## Evaluation Metrics

| Metric          | Description                          |
|-----------------|--------------------------------------|
| Faithfulness    | Is answer grounded in context?       |
| Relevance       | Is retrieved context relevant?       |
| Precision       | Relevant chunks / Total retrieved    |
| Recall          | Relevant chunks / Total relevant     |
| NDCG            | Normalized Discounted Cumulative Gain|
