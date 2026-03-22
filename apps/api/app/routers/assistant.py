from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from uuid import UUID

from app.database import get_db
from app.schemas.assistant import SessionCreateResponse
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    StartConversationResponse,
    SendMessageResponse,
    ProfileSnapshot,
    PhotoInfo,
    ProfileViewData,
)
from app.services.assistant import AssistantService
from app.services.openai_service import OpenAIService
from app.services.vector_service import VectorService, MockVectorService
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])


def get_openai_service() -> OpenAIService:
    """Dependency for OpenAI service."""
    return OpenAIService()


def get_vector_service():
    """Dependency for vector service."""
    try:
        return VectorService()
    except Exception:
        return MockVectorService()


@router.post("/session", response_model=SessionCreateResponse)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> SessionCreateResponse:
    """Create a new session for the authenticated user."""
    service = AssistantService(db, openai_service)
    session_id = service.create_session(current_user.id)
    return SessionCreateResponse(session_id=session_id, status="created")


@router.post("/session/{session_id}/start", response_model=StartConversationResponse)
async def start_conversation(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> StartConversationResponse:
    """Start conversation with initial questions."""
    service = AssistantService(db, openai_service)

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = service.start_conversation(session_id)
    return StartConversationResponse(
        messages=[MessageResponse.model_validate(msg) for msg in messages]
    )


@router.post("/session/{session_id}/message", response_model=SendMessageResponse)
async def send_message(
    session_id: UUID,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service),
    vector_service=Depends(get_vector_service),
) -> SendMessageResponse:
    """Send a user message and get assistant response."""
    service = AssistantService(db, openai_service, vector_service)

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = service.send_message(session_id, request.content)

    user_msg = result["user_message"]
    assistant_msg = result["assistant_message"]
    profile_ready = result["profile_ready"]
    analysis = result["analysis"]
    intent = result["intent"]
    profile_view_data = result["profile_view_data"]

    profile = service.profile_service.get_profile(session_id)
    snapshot = None
    if profile:
        readiness = analysis.get("profile_readiness", None) if analysis else None
        snapshot = ProfileSnapshot(
            age=profile.age,
            gender=profile.gender,
            metrics=profile.metrics,
            communication_style=profile.communication_style,
            attachment_style=profile.attachment_style,
            partner_preferences=profile.partner_preferences,
            values=profile.values,
            profile_readiness=readiness,
        )

    pv = None
    if profile_view_data:
        photos = [
            PhotoInfo(
                id=p["id"],
                url=p["url"],
                vibe_description=p.get("vibe_description"),
                vibe_tags=p.get("vibe_tags"),
            )
            for p in profile_view_data.get("photos", [])
        ]
        pv = ProfileViewData(
            age=profile_view_data.get("age"),
            gender=profile_view_data.get("gender"),
            metrics=profile_view_data.get("metrics"),
            communication_style=profile_view_data.get("communication_style"),
            attachment_style=profile_view_data.get("attachment_style"),
            partner_preferences=profile_view_data.get("partner_preferences"),
            values=profile_view_data.get("values"),
            vibe_tags=profile_view_data.get("vibe_tags"),
            photos=photos,
        )

    return SendMessageResponse(
        user_message=MessageResponse.model_validate(user_msg),
        assistant_message=MessageResponse.model_validate(assistant_msg),
        profile_ready=profile_ready,
        profile_snapshot=snapshot,
        intent=intent,
        profile_view=pv,
    )


@router.get("/session/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> list[MessageResponse]:
    """Get all messages for a session in chronological order."""
    service = AssistantService(db, openai_service)

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = service.get_messages(session_id)
    return [MessageResponse.model_validate(msg) for msg in messages]


@router.get("/session", response_model=SessionCreateResponse)
async def get_or_create_user_session(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> SessionCreateResponse:
    """Get the latest session for authenticated user, or create a new one if none exists."""
    service = AssistantService(db, openai_service)

    session = service.get_user_latest_session(current_user.id)

    if session:
        return SessionCreateResponse(session_id=session.id, status="existing")

    session_id = service.create_session(current_user.id)
    return SessionCreateResponse(session_id=session_id, status="created")
