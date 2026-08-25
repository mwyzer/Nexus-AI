from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentSchema(BaseModel):
    id: UUID
    knowledge_base_id: UUID
    filename: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    doc_metadata: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    document: DocumentSchema
    task_id: str
