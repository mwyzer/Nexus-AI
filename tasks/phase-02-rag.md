# Phase 02 — RAG (Retrieval-Augmented Generation)

## Goal

Implement the full RAG pipeline: document ingestion, chunking, embedding, vector storage, semantic/hybrid search, and answer generation with citations.

## Prerequisites

- Phase 01 (Foundation) complete
- PostgreSQL + pgvector running

## Tasks

### 2.1 — Document Ingestion Pipeline
- [ ] Implement document parser (PDF, Markdown, TXT, HTML)
- [ ] Implement text extraction and cleaning
- [ ] Create document upload API endpoint
- [ ] Create Celery task for async document processing
- [ ] Add document status tracking (pending → processing → ready → error)
- [ ] Implement file type validation and size limits

### 2.2 — Chunking Strategies
- [ ] Implement FixedSizeChunker
- [ ] Implement RecursiveChunker
- [ ] Implement SemanticChunker
- [ ] Implement MarkdownHeaderChunker
- [ ] Create ChunkerFactory for strategy selection
- [ ] Add chunk overlap configuration
- [ ] Write unit tests for all chunkers

### 2.3 — Embedding Generation
- [ ] Implement OpenAI embedding provider
- [ ] Implement Ollama embedding provider (local)
- [ ] Create embedding abstraction layer
- [ ] Implement batch embedding generation
- [ ] Add embedding caching for repeated chunks
- [ ] Handle rate limits and retries

### 2.4 — Vector Store (pgvector)
- [ ] Create pgvector extension setup migration
- [ ] Create chunks and chunk_embeddings tables
- [ ] Implement vector store CRUD operations
- [ ] Create HNSW index for fast similarity search
- [ ] Implement cosine similarity search
- [ ] Add metadata filtering support
- [ ] Implement batch insert for embeddings

### 2.5 — Search Implementation
- [ ] Implement semantic search (vector similarity)
- [ ] Implement keyword search (PostgreSQL full-text)
- [ ] Implement hybrid search with configurable weights
- [ ] Add score threshold filtering
- [ ] Add metadata-based filtering
- [ ] Add pagination support
- [ ] Implement search result re-ranking

### 2.6 — Answer Generation
- [ ] Create RAG prompt template with context injection
- [ ] Implement generate-answer endpoint
- [ ] Add citation extraction and formatting
- [ ] Add confidence scoring
- [ ] Implement streaming answer generation
- [ ] Add fallback when no relevant context found

### 2.7 — Knowledge Base Management (Gateway + Frontend)
- [ ] **Gateway**: Knowledge base CRUD endpoints
- [ ] **Gateway**: Document management endpoints
- [ ] **Frontend**: Knowledge base list page
- [ ] **Frontend**: Knowledge base detail page
- [ ] **Frontend**: Document upload with drag-and-drop
- [ ] **Frontend**: Document list with status indicators
- [ ] **Frontend**: Search interface with results display

### 2.8 — Testing
- [ ] Unit tests for all chunkers
- [ ] Unit tests for embedders
- [ ] Integration tests for full RAG pipeline
- [ ] Search quality tests with known dataset
- [ ] Performance tests (search latency < 500ms)

## Acceptance Criteria

- [ ] Upload a PDF → chunks created → embeddings stored → searchable
- [ ] Semantic search returns relevant results
- [ ] Hybrid search outperforms pure semantic on mixed queries
- [ ] Answer generation includes correct citations
- [ ] Streaming responses work for long answers
- [ ] Search latency < 500ms for KB with 10k chunks
- [ ] All tests pass

## Estimated Effort

4-6 days for a single developer.
