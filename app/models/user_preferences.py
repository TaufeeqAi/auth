### backend/app/models/user_preferences.py
"""User theme and app preferences"""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseModel


class UserPreferences(BaseModel):
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Theme preferences
    theme_mode = Column(String(20), default="system")  # light, dark, system
    primary_color = Column(String(7), default="#2196F3")  # Hex color
    accent_color = Column(String(7), default="#FF4081")   # Hex color
    
    # Notification preferences
    push_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    meeting_reminders = Column(Boolean, default=True)
    summary_notifications = Column(Boolean, default=True)
    
    # App preferences
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    date_format = Column(String(20), default="MM/dd/yyyy")
    time_format = Column(String(10), default="12h")  # 12h or 24h
    
    # Meeting preferences
    default_meeting_duration = Column(Integer, default=60)  # minutes
    auto_join_meetings = Column(Boolean, default=False)
    record_meetings_by_default = Column(Boolean, default=False)
    
    # Privacy preferences
    analytics_enabled = Column(Boolean, default=True)
    crash_reporting = Column(Boolean, default=True)
    
    # Custom settings (JSON string)
    custom_settings = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="preferences")