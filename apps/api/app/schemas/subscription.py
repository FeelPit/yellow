from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class SubscriptionResponse(BaseModel):
    active: bool
    plan: Optional[str] = None
    expires_at: Optional[datetime] = None
    free_chats_remaining: int


class AccessCheckResponse(BaseModel):
    can_message: bool
    reason: str  # "subscription", "mutual_like", "free_message", "blocked"
