### backend/app/repositories/token_repository.py
"""Token management repository"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from datetime import datetime

from ..models.refresh_token import RefreshToken
from .base import BaseRepository


class TokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash"""
        query = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_active == True,
            RefreshToken.expires_at > datetime.utcnow()
        )
        return await self.db.scalar(query)

    async def get_user_tokens(self, user_id: str, device_id: str = None) -> List[RefreshToken]:
        """Get all active tokens for user"""
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_active == True
        )
        
        if device_id:
            query = query.where(RefreshToken.device_id == device_id)
            
        result = await self.db.execute(query)
        return result.scalars().all()

    async def revoke_token(self, token_hash: str) -> bool:
        """Revoke a refresh token"""
        query = update(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        ).values(is_active=False)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def revoke_user_tokens(self, user_id: str, exclude_device: str = None) -> int:
        """Revoke all user tokens except for specified device"""
        query = update(RefreshToken).where(RefreshToken.user_id == user_id)
        
        if exclude_device:
            query = query.where(RefreshToken.device_id != exclude_device)
            
        query = query.values(is_active=False)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens"""
        query = delete(RefreshToken).where(
            RefreshToken.expires_at < datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount