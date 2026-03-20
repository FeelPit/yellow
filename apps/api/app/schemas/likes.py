from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class LikeResponse(BaseModel):
    id: UUID
    user_id: UUID
    liked_user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MutualLikeResponse(BaseModel):
    user_id: UUID
    username: str


class LikeStatusResponse(BaseModel):
    liked: bool
    mutual: bool
