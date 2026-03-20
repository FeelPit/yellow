import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.session import UUID
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(), ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    thinking = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("Session", back_populates="messages")
