from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ProfileResponse(BaseModel):
    id: UUID
    session_id: UUID
    age: Optional[int]
    gender: Optional[str]
    looking_for: Optional[str]
    communication_style: Optional[str]
    attachment_style: Optional[str]
    partner_preferences: Optional[str]
    values: Optional[str]
    metrics: Optional[dict] = None
    vibe_tags: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
