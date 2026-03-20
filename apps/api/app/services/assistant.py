from sqlalchemy.orm import Session as DBSession
from uuid import UUID
from typing import Optional

from app.models.session import Session
from app.models.message import Message
from app.models.photo import Photo
from app.services.openai_service import OpenAIServiceProtocol
from app.services.profile_service import ProfileService
from app.services.vector_service import VectorService, MockVectorService


class AssistantService:
    def __init__(
        self,
        db: DBSession,
        openai_service: Optional[OpenAIServiceProtocol] = None,
        vector_service: Optional[VectorService] = None,
    ):
        self.db = db
        self.openai_service = openai_service
        self.vector_service = vector_service or MockVectorService()
        if openai_service:
            self.profile_service = ProfileService(db, openai_service, vector_service)

    def create_session(self, user_id: UUID) -> UUID:
        """Create a new session for a user."""
        session = Session(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session.id

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        return self.db.query(Session).filter_by(id=session_id).first()

    def start_conversation(self, session_id: UUID) -> list[Message]:
        """Start conversation with initial question."""
        existing_messages = self.db.query(Message).filter_by(
            session_id=session_id
        ).first()

        if existing_messages:
            return self.db.query(Message).filter_by(
                session_id=session_id
            ).order_by(Message.created_at).all()

        question = self.openai_service.generate_initial_question()

        message = Message(
            session_id=session_id,
            role="assistant",
            content=question
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        self.profile_service.get_or_create_profile(session_id)

        return [message]

    def send_message(self, session_id: UUID, content: str) -> dict:
        """
        Send user message and get assistant response.
        Returns dict with: user_message, assistant_message, profile_ready, analysis, intent, profile_view_data
        """
        intent = self.openai_service.detect_intent(content)

        if intent == "photo_manage":
            return self._handle_photo_manage_intent(session_id, content)

        if intent == "view_profile":
            return self._handle_view_profile_intent(session_id, content)

        return self._handle_normal_message(session_id, content)

    def _handle_photo_manage_intent(self, session_id: UUID, content: str) -> dict:
        user_message = self._save_user_message(session_id, content)

        assistant_content = (
            "Sure! Use the camera button below to upload or manage your photos. "
            "You can have up to 3 photos — they help me understand your vibe and "
            "match you with people who share a similar energy."
        )
        assistant_message = Message(
            session_id=session_id, role="assistant", content=assistant_content
        )
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(assistant_message)

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "profile_ready": False,
            "analysis": None,
            "intent": "photo_manage",
            "profile_view_data": None,
        }

    def _handle_view_profile_intent(self, session_id: UUID, content: str) -> dict:
        user_message = self._save_user_message(session_id, content)

        profile = self.profile_service.get_or_create_profile(session_id)
        photos = self.db.query(Photo).filter_by(user_id=profile.user_id).order_by(Photo.order).all()

        photo_list = []
        for p in photos:
            photo_list.append({
                "id": str(p.id),
                "url": f"/api/v1/photos/{p.id}/file",
                "vibe_description": p.vibe_description,
                "vibe_tags": p.vibe_tags,
            })

        profile_view_data = {
            "age": profile.age,
            "gender": profile.gender,
            "metrics": profile.metrics,
            "communication_style": profile.communication_style,
            "attachment_style": profile.attachment_style,
            "partner_preferences": profile.partner_preferences,
            "values": profile.values,
            "vibe_tags": profile.vibe_tags,
            "photos": photo_list,
        }

        lines = ["Here's how your profile looks right now:\n"]
        if profile.age:
            lines.append(f"Age: {profile.age}")
        if profile.gender:
            lines.append(f"Gender: {profile.gender}")
        if profile.communication_style:
            lines.append(f"Communication: {profile.communication_style}")
        if profile.values:
            lines.append(f"Values: {profile.values}")
        if profile.vibe_tags:
            lines.append(f"Vibe: {', '.join(profile.vibe_tags)}")
        if not photos:
            lines.append("\nNo photos yet — use the camera button to add some!")
        else:
            lines.append(f"\n{len(photos)} photo(s) uploaded.")

        assistant_content = "\n".join(lines)
        assistant_message = Message(
            session_id=session_id, role="assistant", content=assistant_content
        )
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(assistant_message)

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "profile_ready": bool(profile.values and profile.communication_style),
            "analysis": None,
            "intent": "view_profile",
            "profile_view_data": profile_view_data,
        }

    def _handle_normal_message(self, session_id: UUID, content: str) -> dict:
        user_message = self._save_user_message(session_id, content)

        self.vector_service.store_message(
            session_id=str(session_id),
            message_id=str(user_message.id),
            content=content,
            role="user",
        )

        messages = self.db.query(Message).filter_by(
            session_id=session_id
        ).order_by(Message.created_at).all()

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        profile = self.profile_service.get_or_create_profile(session_id)
        analysis = self.openai_service.analyze_message(
            conversation_history, profile.metrics
        )

        user_msg_count = len([m for m in messages if m.role == "user"])
        if user_msg_count == 1:
            try:
                basic_info = self.openai_service.extract_basic_info(content)
                self.profile_service.update_basic_info(session_id, basic_info)
            except Exception:
                pass

        updated_profile = self.profile_service.evolve_profile(session_id, analysis)
        profile_ready = bool(updated_profile.values and updated_profile.communication_style)

        # Check if we should nudge user to upload a photo (once, after 3+ messages)
        photo_count = self.db.query(Photo).filter_by(user_id=updated_profile.user_id).count()
        already_nudged = any(
            "camera button" in msg.content for msg in messages if msg.role == "assistant"
        )
        photo_nudge = ""
        if user_msg_count >= 3 and photo_count == 0 and not already_nudged:
            photo_nudge = (
                "\n\nBy the way — if you share a photo, I can pick up on your vibe "
                "and match you with people who have a similar energy. Not about looks — "
                "more about the aesthetic. You can upload up to 3 photos with the camera button."
            )

        assistant_content = self.openai_service.generate_next_question(conversation_history)
        if photo_nudge:
            assistant_content += photo_nudge

        thinking_text = analysis.get("thinking", "")

        assistant_message = Message(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            thinking=thinking_text,
        )
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(assistant_message)

        self.vector_service.store_message(
            session_id=str(session_id),
            message_id=str(assistant_message.id),
            content=assistant_content,
            role="assistant",
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "profile_ready": profile_ready,
            "analysis": analysis,
            "intent": None,
            "profile_view_data": None,
        }

    def _save_user_message(self, session_id: UUID, content: str) -> Message:
        msg = Message(session_id=session_id, role="user", content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, session_id: UUID) -> list[Message]:
        """Get all messages for a session in chronological order."""
        return self.db.query(Message).filter_by(
            session_id=session_id
        ).order_by(Message.created_at).all()

    def get_user_latest_session(self, user_id: UUID) -> Optional[Session]:
        """Get the latest session for a user."""
        return self.db.query(Session).filter_by(
            user_id=user_id
        ).order_by(Session.created_at.desc()).first()
