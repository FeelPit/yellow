import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship

from app.models.session import UUID
from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(), ForeignKey("sessions.id"), nullable=False, unique=True, index=True)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic info
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)  # male, female, non-binary, other
    looking_for = Column(String(50), nullable=True)  # male, female, any
    
    # Structured profile data
    communication_style = Column(Text, nullable=True)
    attachment_style = Column(Text, nullable=True)
    partner_preferences = Column(Text, nullable=True)
    values = Column(Text, nullable=True)
    
    # Numeric personality metrics (0-100 scale)
    metrics = Column(JSON, nullable=True, default=dict)
    
    # Aggregated vibe tags from photos
    vibe_tags = Column(JSON, nullable=True)

    # Raw data for future use
    raw_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="profile")
