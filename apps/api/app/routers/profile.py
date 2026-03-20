from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from uuid import UUID

from app.database import get_db
from app.schemas.profile import ProfileResponse
from app.services.profile_service import ProfileService
from app.services.openai_service import OpenAIService
from app.services.assistant import AssistantService
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


def get_openai_service() -> OpenAIService:
    """Dependency for OpenAI service."""
    return OpenAIService()


@router.get("/{session_id}", response_model=ProfileResponse)
async def get_profile(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> ProfileResponse:
    """Get profile for a session."""
    # Check if session exists and belongs to user
    assistant_service = AssistantService(db, openai_service)
    session = assistant_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get profile
    profile_service = ProfileService(db, openai_service)
    profile = profile_service.get_profile(session_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return ProfileResponse.model_validate(profile)
