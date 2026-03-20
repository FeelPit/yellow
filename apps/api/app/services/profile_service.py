from sqlalchemy.orm import Session as DBSession
from uuid import UUID
from typing import Optional

from app.models.profile import Profile
from app.models.message import Message
from app.services.openai_service import OpenAIServiceProtocol, DEFAULT_TRAITS, TRAIT_KEYS


class ProfileService:
    def __init__(self, db: DBSession, openai_service: OpenAIServiceProtocol, vector_service=None):
        self.db = db
        self.openai_service = openai_service
        self.vector_service = vector_service

    def get_profile(self, session_id: UUID) -> Optional[Profile]:
        """Get profile for a session."""
        return self.db.query(Profile).filter_by(session_id=session_id).first()

    def get_or_create_profile(self, session_id: UUID) -> Profile:
        """Get existing profile or create an empty one."""
        profile = self.get_profile(session_id)
        if profile:
            return profile

        from app.models.session import Session
        session = self.db.query(Session).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        profile = Profile(
            session_id=session_id,
            user_id=session.user_id,
            metrics=dict(DEFAULT_TRAITS),
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def evolve_profile(self, session_id: UUID, analysis: dict) -> Profile:
        """Update profile incrementally based on analysis result."""
        profile = self.get_or_create_profile(session_id)

        new_traits = analysis.get("traits", {})
        current = profile.metrics or dict(DEFAULT_TRAITS)
        for key in TRAIT_KEYS:
            val = new_traits.get(key)
            if val is not None:
                current[key] = val
        profile.metrics = current

        updates = analysis.get("profile_updates", {})
        if updates.get("communication_style"):
            profile.communication_style = updates["communication_style"]
        if updates.get("attachment_style"):
            profile.attachment_style = updates["attachment_style"]
        if updates.get("partner_preferences"):
            profile.partner_preferences = updates["partner_preferences"]
        if updates.get("values"):
            profile.values = updates["values"]

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(profile, "metrics")

        self.db.commit()
        self.db.refresh(profile)

        if self.vector_service:
            self._sync_profile_embedding(profile)

        return profile

    def _sync_profile_embedding(self, profile: Profile):
        """Build a text representation of the profile and store it as an embedding."""
        parts = []
        traits = profile.metrics or {}
        for key in TRAIT_KEYS:
            val = traits.get(key)
            if val:
                parts.append(f"{key}: {val}")
        for field in ["communication_style", "attachment_style", "partner_preferences", "values"]:
            val = getattr(profile, field, None)
            if val:
                parts.append(f"{field}: {val}")
        if parts:
            text = " | ".join(parts)
            self.vector_service.upsert_profile_embedding(str(profile.user_id), text)

    def update_basic_info(self, session_id: UUID, basic_info: dict) -> Profile:
        """Update age/gender/looking_for on the profile."""
        profile = self.get_or_create_profile(session_id)
        if basic_info.get("age"):
            profile.age = basic_info["age"]
        if basic_info.get("gender"):
            profile.gender = basic_info["gender"]
        if basic_info.get("looking_for"):
            profile.looking_for = basic_info["looking_for"]
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def should_create_profile(self, session_id: UUID) -> bool:
        """Check if we should finalize profile (legacy, now always evolving)."""
        existing_profile = self.get_profile(session_id)
        if existing_profile and existing_profile.values:
            return False

        user_messages_count = self.db.query(Message).filter_by(
            session_id=session_id,
            role="user"
        ).count()

        return self.openai_service.should_create_profile(user_messages_count)

    def create_profile(self, session_id: UUID) -> Profile:
        """Finalize a full profile based on conversation (legacy flow)."""
        from app.models.session import Session

        session = self.db.query(Session).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        messages = self.db.query(Message).filter_by(
            session_id=session_id
        ).order_by(Message.created_at).all()

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        first_user_message = next((msg for msg in messages if msg.role == "user"), None)
        basic_info = {}
        if first_user_message:
            try:
                basic_info = self.openai_service.extract_basic_info(first_user_message.content)
            except Exception as e:
                print(f"Failed to extract basic info: {e}")
                basic_info = {"age": None, "gender": None, "looking_for": None}

        profile_data = self.openai_service.generate_profile(conversation_history)

        profile = self.get_or_create_profile(session_id)
        profile.age = basic_info.get("age") or profile.age
        profile.gender = basic_info.get("gender") or profile.gender
        profile.looking_for = basic_info.get("looking_for") or profile.looking_for
        profile.communication_style = profile_data["communication_style"]
        profile.attachment_style = profile_data["attachment_style"]
        profile.partner_preferences = profile_data["partner_preferences"]
        profile.values = profile_data["values"]
        profile.raw_data = profile_data

        self.db.commit()
        self.db.refresh(profile)
        return profile
