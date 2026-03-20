from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from uuid import UUID

from app.database import get_db
from app.schemas.matches import MatchResponse, MatchListResponse, ProfileResponse
from app.schemas.profile import ProfileResponse as ProfileSchemaResponse
from app.services.matching_service import MatchingService
from app.services.vector_service import VectorService, MockVectorService
from app.models.profile import Profile
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["matches"])


def get_vector_service():
    try:
        return VectorService()
    except Exception:
        return MockVectorService()


@router.get("/users/{user_id}/profile", response_model=ProfileSchemaResponse)
def get_user_profile(
    user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get profile for a specific user."""
    profile = db.query(Profile).filter_by(user_id=user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.get("/users/{user_id}/matches", response_model=MatchListResponse)
def get_user_matches(
    user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vector_service=Depends(get_vector_service),
    limit: int = 5
):
    """Get matches for a user using vector similarity on trait insights."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view your own matches")

    matching_service = MatchingService(db, vector_service)
    matches = matching_service.get_matches(user_id, limit=min(limit, 5))

    match_responses = []
    for user, profile, score, explanation in matches:
        match_responses.append(
            MatchResponse(
                user_id=user.id,
                username=user.username,
                profile=ProfileResponse(
                    age=profile.age,
                    gender=profile.gender,
                    communication_style=profile.communication_style,
                    attachment_style=profile.attachment_style,
                    partner_preferences=profile.partner_preferences,
                    values=profile.values,
                ),
                match_score=score,
                match_explanation=explanation,
            )
        )

    return MatchListResponse(
        matches=match_responses,
        total=len(match_responses)
    )
