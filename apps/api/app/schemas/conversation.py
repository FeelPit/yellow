from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class DirectMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class DirectMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: UUID
    other_user_id: UUID
    other_username: str
    access_reason: str
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    id: UUID
    other_user_id: UUID
    other_username: str
    access_reason: str
    messages: list[DirectMessageResponse]


class AdvisorRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AdvisorResponse(BaseModel):
    answer: str
