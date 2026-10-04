# Phase 02 — RAG (Retrieval-Augmented Generation)

## Goal

Implement the full RAG pipeline: document ingestion, chunking, embedding, vector storage, semantic/hybrid search, and answer generation with citations.

## Prerequisites

- Phase 01 (Foundation) complete
- PostgreSQL + pgvector running

## Tasks

### 2.1 — Document Ingestion Pipeline
- [x] Implement document parser (PDF, Markdown, TXT, HTML) — `app/rag/parsing.py`
- [x] Implement text extraction and cleaning — `app/rag/parsing.py`
- [x] Create document upload API endpoint — `app/api/v1/documents.py`
- [x] Create Celery task for async document processing — `app/worker/tasks.py`
- [x] Add document status tracking (pending → processing → ready → error) — `app/models/document.py` + `app/rag/ingestion.py`
- [x] Implement file type validation and size limits — `app/api/v1/documents.py` + `MAX_FILE_SIZE_BYTES` in `ingestion.py`

### 2.2 — Chunking Strategies
- [x] Implement FixedSizeChunker — `app/rag/chunking.py`
- [x] Implement RecursiveChunker — `app/rag/chunking.py`
- [x] Implement SemanticChunker — `app/rag/chunking.py`
- [x] Implement MarkdownHeaderChunker — `app/rag/chunking.py`
- [x] Create ChunkerFactory for strategy selection — `get_chunker()`
- [x] Add chunk overlap configuration — present on all four chunkers
- [x] Write unit tests for all chunkers — `tests/test_chunking.py`

### 2.3 — Embedding Generation
- [x] Implement OpenAI embedding provider — `app/rag/embedding.py`
- [x] Implement Ollama embedding provider (local) — `app/rag/embedding.py`
- [x] Create embedding abstraction layer — `Embedder` ABC + `get_embedder()`
- [ ] Implement batch embedding generation — OpenAI path batches via `aembed_documents`, but `OllamaEmbedder.embed` loops one HTTP call per text; not a real batch for the Ollama path
- [ ] Add embedding caching for repeated chunks — not implemented
- [ ] Handle rate limits and retries — no retry/backoff on either provider

### 2.4 — Vector Store (pgvector)
- [x] Create pgvector extension setup migration — `alembic/versions/0001_rag_core.py`
- [x] Create chunks and chunk_embeddings tables — `0001_rag_core.py`
- [x] Implement vector store CRUD operations — `app/rag/vector_store.py` (`add_chunks`, `delete_document_chunks`)
- [x] Create HNSW index for fast similarity search — `idx_chunk_embeddings_hnsw` in `0001_rag_core.py`
- [x] Implement cosine similarity search — `semantic_search` via `cosine_distance`
- [ ] Add metadata filtering support — search is scoped by `knowledge_base_id` only; no chunk/document metadata filter
- [x] Implement batch insert for embeddings — `add_chunks` persists a document's whole chunk/embedding batch in one flush

### 2.5 — Search Implementation
- [x] Implement semantic search (vector similarity) — `vector_store.semantic_search`
- [x] Implement keyword search (PostgreSQL full-text) — `vector_store.keyword_search` via `tsvector`/`tsquery`
- [x] Implement hybrid search with configurable weights — `vector_store.hybrid_search` (`hybrid_weight`)
- [x] Add score threshold filtering — applied in `semantic_search`, `keyword_search`, and `hybrid_search` (on the final blended score)
- [ ] Add metadata-based filtering — not implemented
- [ ] Add pagination support — `SearchQuery` has `top_k` only, no offset/cursor
- [ ] Implement search result re-ranking — hybrid blending normalizes/combines scores but there's no distinct re-rank step

### 2.6 — Answer Generation
- [x] Create RAG prompt template with context injection — `app/rag/generation.py` `PROMPT_TEMPLATE`
- [x] Implement generate-answer endpoint — `app/api/v1/rag.py`
- [x] Add citation extraction and formatting — `Citation` schema + `_build_context`
- [x] Add confidence scoring — mean of result scores
- [ ] Implement streaming answer generation — both `_complete_openai` and `_complete_ollama` are non-streaming (`stream: False` explicitly set for Ollama)
- [x] Add fallback when no relevant context found — `NO_CONTEXT_ANSWER`

### 2.7 — Knowledge Base Management (Gateway + Frontend)
- [x] **Gateway**: Knowledge base CRUD endpoints — `gateway/src/rag/knowledge-bases.controller.ts`
- [x] **Gateway**: Document management endpoints — `gateway/src/rag/documents.controller.ts`
- [ ] **Frontend**: Knowledge base list page — not started
- [ ] **Frontend**: Knowledge base detail page — not started
- [ ] **Frontend**: Document upload with drag-and-drop — not started
- [ ] **Frontend**: Document list with status indicators — not started
- [ ] **Frontend**: Search interface with results display — not started

### 2.8 — Testing
- [x] Unit tests for all chunkers — `tests/test_chunking.py`
- [ ] Unit tests for embedders — not started
- [ ] Integration tests for full RAG pipeline — not started
- [ ] Search quality tests with known dataset — not started
- [ ] Performance tests (search latency < 500ms) — not started

## Acceptance Criteria

> Unchecked below pending an actual run against a live stack (`docker compose up`) — the code paths exist end-to-end, but none of this has been exercised/verified yet.

- [ ] Upload a PDF → chunks created → embeddings stored → searchable
- [ ] Semantic search returns relevant results
- [ ] Hybrid search outperforms pure semantic on mixed queries
- [ ] Answer generation includes correct citations
- [ ] Streaming responses work for long answers — blocked: streaming isn't implemented (see 2.6)
- [ ] Search latency < 500ms for KB with 10k chunks
- [ ] All tests pass

## Estimated Effort

4-6 days for a single developer.
