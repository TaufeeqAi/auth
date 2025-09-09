### backend/app/repositories/preferences_repository.py
"""User preferences data access layer"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..models.user_preferences import UserPreferences
from .base import BaseRepository


class PreferencesRepository(BaseRepository[UserPreferences]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserPreferences, db)

    async def get_by_user_id(self, user_id: str) -> Optional[UserPreferences]:
        """Get preferences by user ID"""
        query = select(UserPreferences).where(UserPreferences.user_id == user_id)
        return await self.db.scalar(query)

    async def create_default(self, user_id: str) -> UserPreferences:
        """Create default preferences for user"""
        preferences = UserPreferences(user_id=user_id)
        self.db.add(preferences)
        await self.db.commit()
        await self.db.refresh(preferences)
        return preferences
