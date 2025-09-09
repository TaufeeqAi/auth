"""Enhanced JWT authentication service with refresh tokens and eager loading"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ...models.user import User
from ...models.refresh_token import RefreshToken
from ...schemas.auth import TokenResponse, RefreshTokenRequest, UserLogin
from ...core.config import settings
from ...core.security import verify_password


class JWTAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        # The database session is managed by the router, so we don't commit here.
        query = (
            select(User)
            .where(User.email == email)
        )
        result = await self.db.execute(query)
        user: Optional[User] = result.scalar_one_or_none()

        if user and verify_password(password, user.password_hash):
            # Update last login time
            user.last_login = datetime.now(timezone.utc)
            return user
        
        return None

    async def create_tokens(
        self, user: User, device_id: str, remember_me: bool = False
    ) -> TokenResponse:
        """Create access and refresh tokens"""
        # Ensure user is fully loaded to avoid MissingGreenlet
        await self.db.refresh(user)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": datetime.now(timezone.utc) + access_token_expires,
            "type": "access",
        }
        access_token = jwt.encode(
            access_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        # Create refresh token
        refresh_expires_days = 30 if remember_me else 7
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=refresh_expires_days)

        refresh_token = secrets.token_urlsafe(32)
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # Store refresh token in database. No commit here.
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            device_id=device_id,
            expires_at=refresh_token_expires,
        )

        self.db.add(db_refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_token_expires.total_seconds()),
            user_id=str(user.id),
            role=user.role.value,
        )

    async def refresh_access_token(
        self, refresh_request: RefreshTokenRequest
    ) -> Optional[TokenResponse]:
        """Refresh access token using refresh token"""
        # The database session is managed by the router.
        refresh_token_hash = hashlib.sha256(
            refresh_request.refresh_token.encode()
        ).hexdigest()

        # Find valid refresh token
        query = select(RefreshToken).where(
            RefreshToken.token_hash == refresh_token_hash,
            RefreshToken.device_id == refresh_request.device_id,
            RefreshToken.is_active.is_(True),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        db_token = (await self.db.execute(query)).scalar_one_or_none()

        if not db_token:
            return None

        # Get user
        user_query = (
            select(User)
            .where(User.id == db_token.user_id)
        )
        user = (await self.db.execute(user_query)).scalar_one_or_none()

        if not user or not user.is_active:
            return None

        # Update refresh token last used
        db_token.last_used = datetime.now(timezone.utc)

        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": datetime.now(timezone.utc) + access_token_expires,
            "type": "access",
        }
        access_token = jwt.encode(
            access_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_request.refresh_token,
            expires_in=int(access_token_expires.total_seconds()),
            user_id=str(user.id),
            role=user.role.value,
        )

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token"""
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        query = select(RefreshToken).where(
            RefreshToken.token_hash == refresh_token_hash
        )
        db_token = (await self.db.execute(query)).scalar_one_or_none()

        if db_token:
            db_token.is_active = False
            return True

        return False
