
### backend/app/schemas/preferences.py
"""User preferences DTOs"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import re


class UserPreferencesUpdate(BaseModel):
    # Theme preferences
    theme_mode: Optional[str] = Field(None, pattern="^(light|dark|system)$")
    primary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    accent_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    # Notification preferences
    push_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    meeting_reminders: Optional[bool] = None
    summary_notifications: Optional[bool] = None
    
    # App preferences
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)
    time_format: Optional[str] = Field(None, pattern="^(12h|24h)$")
    
    # Meeting preferences
    default_meeting_duration: Optional[int] = Field(None, ge=15, le=480)  # 15 min to 8 hours
    auto_join_meetings: Optional[bool] = None
    record_meetings_by_default: Optional[bool] = None
    
    # Privacy preferences
    analytics_enabled: Optional[bool] = None
    crash_reporting: Optional[bool] = None
    
    # Custom settings
    custom_settings: Optional[Dict[str, Any]] = None


class UserPreferencesResponse(BaseModel):
    id: str
    # Theme preferences
    theme_mode: str
    primary_color: str
    accent_color: str
    
    # Notification preferences
    push_notifications: bool
    email_notifications: bool
    meeting_reminders: bool
    summary_notifications: bool
    
    # App preferences
    language: str
    timezone: str
    date_format: str
    time_format: str
    
    # Meeting preferences
    default_meeting_duration: int
    auto_join_meetings: bool
    record_meetings_by_default: bool
    
    # Privacy preferences
    analytics_enabled: bool
    crash_reporting: bool
    
    # Custom settings
    custom_settings: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True