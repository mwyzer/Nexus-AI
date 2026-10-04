from sqlalchemy.ext.asyncio import AsyncSession

from ..models.document import Document
from ..models.knowledge_base import KnowledgeBase
from ..schemas.chunk import ChunkConfig
from . import vector_store
from .chunking import get_chunker
from .embedding import get_embedder, infer_embedding_provider
from .parsing import UnsupportedFormatError, parse_document

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB, enforced at the API boundary too


class IngestionError(Exception):
    pass


async def ingest_document(session: AsyncSession, document: Document, raw: bytes) -> None:
    """Parse, chunk, embed, and store a document's content. Updates document.status in place."""
    document.status = "processing"
    await session.flush()

    try:
        if len(raw) > MAX_FILE_SIZE_BYTES:
            raise IngestionError(f"File exceeds max size of {MAX_FILE_SIZE_BYTES} bytes")

        kb = await session.get(KnowledgeBase, document.knowledge_base_id)
        if kb is None:
            raise IngestionError("Knowledge base not found")

        parsed = parse_document(raw, document.mime_type or "text/plain")
        if not parsed.text.strip():
            raise IngestionError("No extractable text in document")

        strategy = "markdown" if document.mime_type == "text/markdown" else "recursive"
        config = ChunkConfig(
            strategy=strategy, chunk_size=kb.chunk_size, chunk_overlap=kb.chunk_overlap
        )
        chunks = get_chunker(config).split(parsed.text)
        if not chunks:
            raise IngestionError("Chunking produced no chunks")

        provider = infer_embedding_provider(kb.embedding_model)
        embedder = get_embedder(provider, kb.embedding_model)
        embeddings = await embedder.embed([c.content for c in chunks])

        await vector_store.add_chunks(session, document.id, chunks, embeddings, kb.embedding_model)

        document.status = "ready"
        document.error_message = None
    except (UnsupportedFormatError, IngestionError) as exc:
        document.status = "error"
        document.error_message = str(exc)[:1000]
    except Exception as exc:  # noqa: BLE001 - surface unexpected failures on the document row
        document.status = "error"
        document.error_message = f"Unexpected error: {exc}"[:1000]

    await session.flush()
