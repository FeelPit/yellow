from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import or_, and_
from uuid import UUID
from datetime import datetime
import os

from app.database import get_db
from app.models.user import User
from app.models.like import Like
from app.models.subscription import Subscription
from app.models.conversation import Conversation, DirectMessage
from app.models.profile import Profile
from app.routers.auth import get_current_user
from app.schemas.conversation import (
    DirectMessageCreate,
    DirectMessageResponse,
    ConversationResponse,
    ConversationDetailResponse,
    AdvisorRequest,
    AdvisorResponse,
)
from app.schemas.subscription import AccessCheckResponse, SubscriptionResponse
from app.services.openai_service import OpenAIService, MockOpenAIService


def get_openai_service():
    if os.environ.get("TESTING"):
        return MockOpenAIService()
    return OpenAIService()

router = APIRouter(prefix="/api/v1", tags=["conversations"])


def _has_active_subscription(db: DBSession, user_id: UUID) -> bool:
    sub = db.query(Subscription).filter_by(user_id=user_id, active=True).first()
    if not sub:
        return False
    if sub.expires_at and sub.expires_at < datetime.utcnow():
        sub.active = False
        db.commit()
        return False
    return True


def _has_mutual_like(db: DBSession, user1_id: UUID, user2_id: UUID) -> bool:
    like_a = db.query(Like).filter_by(user_id=user1_id, liked_user_id=user2_id).first()
    like_b = db.query(Like).filter_by(user_id=user2_id, liked_user_id=user1_id).first()
    return like_a is not None and like_b is not None


def _find_conversation(db: DBSession, user1_id: UUID, user2_id: UUID):
    return db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == user1_id, Conversation.user2_id == user2_id),
            and_(Conversation.user1_id == user2_id, Conversation.user2_id == user1_id),
        )
    ).first()


def _check_access(db: DBSession, user: User, target_user_id: UUID) -> tuple[bool, str]:
    """Check if user can start a conversation with target. Returns (can_message, reason)."""
    existing = _find_conversation(db, user.id, target_user_id)
    if existing:
        return True, existing.access_reason

    if _has_active_subscription(db, user.id):
        return True, "subscription"

    if _has_mutual_like(db, user.id, target_user_id):
        return True, "mutual_like"

    if user.free_chats_used < 1:
        return True, "free_message"

    return False, "blocked"


@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription_status(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = db.query(Subscription).filter_by(user_id=current_user.id, active=True).first()
    active = False
    plan = None
    expires_at = None

    if sub:
        if sub.expires_at and sub.expires_at < datetime.utcnow():
            sub.active = False
            db.commit()
        else:
            active = True
            plan = sub.plan
            expires_at = sub.expires_at

    return SubscriptionResponse(
        active=active,
        plan=plan,
        expires_at=expires_at,
        free_chats_remaining=max(0, 1 - current_user.free_chats_used),
    )


@router.get("/conversations/{target_user_id}/access", response_model=AccessCheckResponse)
def check_access(
    target_user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    target = db.query(User).filter_by(id=target_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    can_msg, reason = _check_access(db, current_user, target_user_id)
    return AccessCheckResponse(can_message=can_msg, reason=reason)


@router.post("/conversations/{target_user_id}", response_model=ConversationResponse)
def start_conversation(
    target_user_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    target = db.query(User).filter_by(id=target_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = _find_conversation(db, current_user.id, target_user_id)
    if existing:
        return _build_conversation_response(db, existing, current_user.id)

    can_msg, reason = _check_access(db, current_user, target_user_id)
    if not can_msg:
        raise HTTPException(
            status_code=403,
            detail="Subscribe or exchange likes to start chatting",
        )

    if reason == "free_message":
        current_user.free_chats_used += 1

    conv = Conversation(
        user1_id=current_user.id,
        user2_id=target_user_id,
        access_reason=reason,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    return _build_conversation_response(db, conv, current_user.id)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convs = (
        db.query(Conversation)
        .filter(or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id,
        ))
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return [_build_conversation_response(db, c, current_user.id) for c in convs]


@router.get("/conversations/{conversation_id}/messages", response_model=list[DirectMessageResponse])
def get_conversation_messages(
    conversation_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.id not in (conv.user1_id, conv.user2_id):
        raise HTTPException(status_code=403, detail="Access denied")

    msgs = (
        db.query(DirectMessage)
        .filter_by(conversation_id=conversation_id)
        .order_by(DirectMessage.created_at)
        .all()
    )
    return msgs


@router.post("/conversations/{conversation_id}/messages", response_model=DirectMessageResponse)
def send_direct_message(
    conversation_id: UUID,
    request: DirectMessageCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.id not in (conv.user1_id, conv.user2_id):
        raise HTTPException(status_code=403, detail="Access denied")

    msg = DirectMessage(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=request.content,
    )
    db.add(msg)
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(msg)
    return msg


@router.post("/conversations/{conversation_id}/advisor", response_model=AdvisorResponse)
def ask_advisor(
    conversation_id: UUID,
    request: AdvisorRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    openai_service=Depends(get_openai_service),
):
    conv = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.id not in (conv.user1_id, conv.user2_id):
        raise HTTPException(status_code=403, detail="Access denied")

    other_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
    other_user = db.query(User).filter_by(id=other_id).first()
    other_profile = db.query(Profile).filter_by(user_id=other_id).first()

    profile_dict = {}
    if other_profile:
        if other_profile.metrics:
            for k, v in other_profile.metrics.items():
                if v:
                    profile_dict[k] = v
        for field in ("communication_style", "attachment_style", "values", "partner_preferences"):
            val = getattr(other_profile, field, None)
            if val:
                profile_dict[field] = val
        if other_profile.vibe_tags:
            profile_dict["vibe"] = ", ".join(other_profile.vibe_tags)

    msgs = (
        db.query(DirectMessage)
        .filter_by(conversation_id=conversation_id)
        .order_by(DirectMessage.created_at)
        .all()
    )

    other_name = other_user.username if other_user else "them"
    conversation_messages = []
    for m in msgs:
        label = "You" if m.sender_id == current_user.id else other_name
        conversation_messages.append({"label": label, "content": m.content})

    answer = openai_service.chat_advisor(conversation_messages, profile_dict, request.question)
    return AdvisorResponse(answer=answer)


def _build_conversation_response(db: DBSession, conv: Conversation, my_id: UUID) -> ConversationResponse:
    other_id = conv.user2_id if conv.user1_id == my_id else conv.user1_id
    other_user = db.query(User).filter_by(id=other_id).first()

    last_msg = (
        db.query(DirectMessage)
        .filter_by(conversation_id=conv.id)
        .order_by(DirectMessage.created_at.desc())
        .first()
    )

    return ConversationResponse(
        id=conv.id,
        other_user_id=other_id,
        other_username=other_user.username if other_user else "deleted",
        access_reason=conv.access_reason,
        last_message=last_msg.content if last_msg else None,
        last_message_at=last_msg.created_at if last_msg else None,
        created_at=conv.created_at,
    )
