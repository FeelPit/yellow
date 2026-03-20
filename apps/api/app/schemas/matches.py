from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class ProfileResponse(BaseModel):
    """Profile data for matching."""
    age: Optional[int] = None
    gender: Optional[str] = None
    communication_style: Optional[str] = None
    attachment_style: Optional[str] = None
    partner_preferences: Optional[str] = None
    values: Optional[str] = None
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    """Single match result."""
    user_id: UUID
    username: str
    profile: ProfileResponse
    match_score: float
    match_explanation: str


class MatchListResponse(BaseModel):
    """List of matches."""
    matches: list[MatchResponse]
    total: int
