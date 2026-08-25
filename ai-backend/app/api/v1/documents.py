import base64
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.document import Document
from ...models.knowledge_base import KnowledgeBase
from ...rag.ingestion import MAX_FILE_SIZE_BYTES
from ...schemas.document import DocumentSchema, DocumentUploadResponse
from ...worker.celery_app import celery_app

router = APIRouter()

SUPPORTED_MIME_TYPES = {"application/pdf", "text/markdown", "text/plain", "text/html"}


@router.post("", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    knowledge_base_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    kb = await db.get(KnowledgeBase, knowledge_base_id)
    if kb is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    mime_type = file.content_type or "text/plain"
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {mime_type}")

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds max upload size")
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    document = Document(
        knowledge_base_id=knowledge_base_id,
        filename=file.filename or "untitled",
        mime_type=mime_type,
        file_size=len(raw),
        status="pending",
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    raw_b64 = base64.b64encode(raw).decode("ascii")
    result = celery_app.send_task("ingest_document", args=[str(document.id), raw_b64])

    return DocumentUploadResponse(document=document, task_id=result.id)


@router.get("", response_model=list[DocumentSchema])
async def list_documents(
    knowledge_base_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Document)
        .where(Document.knowledge_base_id == knowledge_base_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars())


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(document)
