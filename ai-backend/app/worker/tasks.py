import asyncio
import base64
from uuid import UUID

from ..core.database import async_session, engine
from ..models.document import Document
from ..rag.ingestion import ingest_document
from .celery_app import celery_app


async def _run_ingestion(document_id: str, raw_b64: str) -> None:
    try:
        async with async_session() as session:
            document = await session.get(Document, UUID(document_id))
            if document is None:
                return
            raw = base64.b64decode(raw_b64)
            await ingest_document(session, document, raw)
            await session.commit()
    finally:
        # Each task run gets its own event loop via asyncio.run(); the engine's
        # pooled connections are bound to that loop and become unusable once it
        # closes, so the pool must be dropped before the next task runs.
        await engine.dispose()


@celery_app.task(name="ingest_document")
def ingest_document_task(document_id: str, raw_b64: str) -> None:
    asyncio.run(_run_ingestion(document_id, raw_b64))
