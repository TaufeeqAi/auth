### backend/app/models/refresh_token.py
"""Refresh token management for JWT authentication"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .base import BaseModel


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(256), nullable=False, unique=True)
    device_id = Column(String(255), nullable=False)
    device_info = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")