from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    thinking: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StartConversationResponse(BaseModel):
    messages: list[MessageResponse]


class ProfileSnapshot(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    metrics: Optional[dict] = None
    communication_style: Optional[str] = None
    attachment_style: Optional[str] = None
    partner_preferences: Optional[str] = None
    values: Optional[str] = None
    profile_readiness: Optional[int] = None


class PhotoInfo(BaseModel):
    id: UUID
    url: str
    vibe_description: Optional[str] = None
    vibe_tags: Optional[list[str]] = None


class ProfileViewData(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    metrics: Optional[dict] = None
    communication_style: Optional[str] = None
    attachment_style: Optional[str] = None
    partner_preferences: Optional[str] = None
    values: Optional[str] = None
    vibe_tags: Optional[list[str]] = None
    photos: list[PhotoInfo] = []


class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    profile_ready: bool
    profile_snapshot: Optional[ProfileSnapshot] = None
    intent: Optional[str] = None
    profile_view: Optional[ProfileViewData] = None
