# 13 — Background Jobs Specification

## Overview

Background job processing is handled by Celery with Redis as the message broker. Long-running or resource-intensive tasks are offloaded from the API layer to worker processes.

## Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  FastAPI  │────→│  Redis   │────→│ Celery Worker │
│  Gateway  │     │ (Broker) │     │              │
└──────────┘     └──────────┘     └──────┬───────┘
                                         │
                                  ┌──────▼───────┐
                                  │  PostgreSQL  │
                                  │  + pgvector  │
                                  └──────────────┘
```

## Celery Configuration

```python
# ai-backend/app/worker/celery_app.py
from celery import Celery

celery_app = Celery(
    "nexus_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.worker.tasks.ingestion",
        "app.worker.tasks.embeddings",
        "app.worker.tasks.evaluation",
        "app.worker.tasks.maintenance",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,       # 1 hour max
    task_soft_time_limit=3300,  # 55 min soft limit
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
)
```

## Task Definitions

### Document Ingestion

```python
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_document(self, document_id: str) -> dict:
    """Process a document: parse → chunk → embed → store."""
    try:
        doc = DocumentService.get(document_id)
        doc.status = "processing"
        
        # 1. Parse
        text = parse_document(doc.filepath, doc.mime_type)
        
        # 2. Chunk
        chunks = chunk_text(text, doc.knowledge_base.chunk_config)
        
        # 3. Embed
        embeddings = generate_embeddings([c.content for c in chunks])
        
        # 4. Store
        store_chunks_with_embeddings(chunks, embeddings, doc.id)
        
        doc.status = "ready"
        return {"chunks": len(chunks), "document_id": document_id}
        
    except Exception as exc:
        doc.status = "error"
        raise self.retry(exc=exc)
```

### Batch Embedding

```python
@celery_app.task(bind=True)
def generate_embeddings_batch(
    self,
    chunk_ids: list[str],
    model: str = "text-embedding-3-small",
) -> dict:
    """Generate embeddings for multiple chunks in batch."""
    chunks = ChunkService.get_by_ids(chunk_ids)
    texts = [c.content for c in chunks]
    
    embeddings = embedding_model.embed_documents(texts, model=model)
    
    # Store in pgvector
    store_embeddings_batch(chunk_ids, embeddings, model)
    
    return {"processed": len(chunk_ids)}
```

### Evaluation Run

```python
@celery_app.task(bind=True)
def run_rag_evaluation(
    self,
    eval_run_id: str,
    dataset_id: str,
    config: dict,
) -> dict:
    """Run RAG evaluation against a dataset."""
    dataset = EvalDatasetService.get(dataset_id)
    pipeline = RAGPipeline.from_config(config)
    
    results = []
    for entry in dataset.entries:
        result = evaluate_single(pipeline, entry)
        results.append(result)
        self.update_state(state="PROGRESS", meta={
            "current": len(results),
            "total": len(dataset.entries),
        })
    
    metrics = aggregate_metrics(results)
    EvalRunService.complete(eval_run_id, metrics)
    
    return metrics.model_dump()
```

### Maintenance Tasks

```python
@celery_app.task
def cleanup_expired_sessions() -> int:
    """Remove expired refresh tokens and sessions."""
    return SessionService.cleanup_expired()

@celery_app.task
def vacuum_audit_logs() -> int:
    """Archive old audit logs per retention policy."""
    return AuditService.apply_retention_policy()

@celery_app.task
def reindex_knowledge_base(kb_id: str) -> dict:
    """Re-index all documents in a knowledge base."""
    kb = KnowledgeBaseService.get(kb_id)
    docs = DocumentService.get_by_kb(kb_id)
    
    for doc in docs:
        ingest_document.delay(str(doc.id))
    
    return {"queued": len(docs), "kb_id": kb_id}
```

## Scheduled Tasks (Celery Beat)

```python
# ai-backend/app/worker/beat_schedule.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "cleanup-sessions-every-hour": {
        "task": "app.worker.tasks.maintenance.cleanup_expired_sessions",
        "schedule": crontab(minute=0),
    },
    "vacuum-audit-logs-daily": {
        "task": "app.worker.tasks.maintenance.vacuum_audit_logs",
        "schedule": crontab(hour=3, minute=0),
    },
    "run-scheduled-evaluations": {
        "task": "app.worker.tasks.evaluation.run_scheduled_evaluations",
        "schedule": crontab(hour=2, minute=0, day_of_week="sunday"),
    },
}
```

## Task Monitoring

```python
# Get task status
GET /api/v1/tasks/{task_id}/status

# Response
{
    "task_id": "abc-123",
    "status": "PROGRESS",  # PENDING, STARTED, PROGRESS, SUCCESS, FAILURE
    "progress": { "current": 42, "total": 100 },
    "result": null,
    "error": null
}
```

## Error Handling & Retry

```python
# Retry with exponential backoff
@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=10,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def resilient_task(self, *args, **kwargs):
    # Task implementation
    pass
```
