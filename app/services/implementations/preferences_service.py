
### backend/app/services/implementations/preferences_service.py
"""User preferences service"""

import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ...models.user_preferences import UserPreferences
from ...schemas.preferences import UserPreferencesUpdate, UserPreferencesResponse


class PreferencesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferencesResponse]:
        """Get user preferences"""
        query = select(UserPreferences).where(UserPreferences.user_id == user_id)
        preferences = await self.db.scalar(query)
        
        if not preferences:
            # Create default preferences
            preferences = await self.create_default_preferences(user_id)
            
        return UserPreferencesResponse.from_orm(preferences)

    async def update_user_preferences(self, user_id: str, preferences_data: UserPreferencesUpdate) -> UserPreferencesResponse:
        """Update user preferences"""
        query = select(UserPreferences).where(UserPreferences.user_id == user_id)
        preferences = await self.db.scalar(query)
        
        if not preferences:
            preferences = await self.create_default_preferences(user_id)
            
        # Update preferences
        for field, value in preferences_data.dict(exclude_unset=True).items():
            if field == "custom_settings" and value:
                value = json.dumps(value)
            setattr(preferences, field, value)
            
        await self.db.commit()
        await self.db.refresh(preferences)
        
        return UserPreferencesResponse.from_orm(preferences)

    async def create_default_preferences(self, user_id: str) -> UserPreferences:
        """Create default preferences for user"""
        preferences = UserPreferences(
            user_id=user_id,
            theme_mode="system",
            primary_color="#2196F3",
            accent_color="#FF4081",
            push_notifications=True,
            email_notifications=True,
            meeting_reminders=True,
            summary_notifications=True,
            language="en",
            timezone="UTC",
            date_format="MM/dd/yyyy",
            time_format="12h",
            default_meeting_duration=60,
            auto_join_meetings=False,
            record_meetings_by_default=False,
            analytics_enabled=True,
            crash_reporting=True
        )
        
        self.db.add(preferences)
        await self.db.commit()
        await self.db.refresh(preferences)
        
        return preferences
