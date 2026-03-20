from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PhotoResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    original_name: str
    vibe_description: Optional[str] = None
    vibe_tags: Optional[list[str]] = None
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    photo: PhotoResponse
    message: str
