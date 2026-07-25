from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserSchema(BaseModel):
    """Schema for user data."""
    id: str
    email: str
    display_name: str
    roles: List[str]
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    service: str
    version: str
    timestamp: str
