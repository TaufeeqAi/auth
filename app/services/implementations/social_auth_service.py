
### backend/app/services/implementations/social_auth_service.py
"""Social authentication service (Google/Apple)"""

import httpx
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, Dict, Any

from ...models.user import User, UserRole
from ...schemas.token import SocialAuthRequest, TokenResponse
from ...core.config import settings
from .jwt_auth_service import JWTAuthService
from .user_service_impl import UserServiceImpl


class SocialAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = JWTAuthService(db)
        self.user_service = UserServiceImpl(db)

    async def authenticate_social(self, auth_data: SocialAuthRequest) -> Optional[TokenResponse]:
        """Authenticate user using social login"""
        try:
            if auth_data.provider == "google":
                user_info = await self._verify_google_token(auth_data.access_token)
            elif auth_data.provider == "apple":
                user_info = await self._verify_apple_token(auth_data.access_token)
            else:
                return None
                
            if not user_info:
                return None
                
            # Find or create user
            user = await self._find_or_create_social_user(user_info, auth_data.provider)
            if not user:
                return None
                
            # Generate device ID if not provided
            device_id = auth_data.device_info.get("device_id") if auth_data.device_info else "social_web"
            
            # Create tokens
            token_response = await self.auth_service.create_tokens(user, device_id)
            
            # Update last login
            await self.db.execute(
                update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
            )
            await self.db.commit()
            
            return token_response
            
        except Exception as e:
            await self.db.rollback()
            return None

    async def _verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
                )
                
                if response.status_code == 200:
                    user_info = response.json()
                    return {
                        "id": user_info.get("id"),
                        "email": user_info.get("email"),
                        "name": user_info.get("name"),
                        "picture": user_info.get("picture"),
                        "verified_email": user_info.get("verified_email", False)
                    }
                    
        except Exception:
            pass
            
        return None

    async def _verify_apple_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Apple OAuth token"""
        # Apple token verification is more complex and requires JWT verification
        # This is a simplified implementation
        try:
            # In production, you would need to:
            # 1. Fetch Apple's public keys
            # 2. Verify JWT signature
            # 3. Validate claims
            
            # For demo purposes, returning mock data
            # Replace with actual Apple Sign In verification
            return {
                "id": "apple_user_id",
                "email": "user@example.com",
                "name": "Apple User",
                "verified_email": True
            }
            
        except Exception:
            pass
            
        return None

    async def _find_or_create_social_user(self, user_info: Dict[str, Any], provider: str) -> Optional[User]:
        """Find existing user or create new one for social login"""
        try:
            # Check if user exists with social ID
            social_id_field = f"{provider}_id"
            user_query = select(User).where(
                getattr(User, social_id_field) == user_info["id"]
            )
            user = await self.db.scalar(user_query)
            
            if user:
                return user
                
            # Check if user exists with email
            email_query = select(User).where(User.email == user_info["email"])
            user = await self.db.scalar(email_query)
            
            if user:
                # Link social account to existing user
                setattr(user, social_id_field, user_info["id"])
                if not user.is_verified and user_info.get("verified_email"):
                    user.is_verified = True
                await self.db.commit()
                return user
                
            # Create new user
            new_user = User(
                email=user_info["email"],
                full_name=user_info.get("name", ""),
                is_verified=user_info.get("verified_email", False),
                avatar_url=user_info.get("picture"),
                role=UserRole.ATTENDEE
            )
            setattr(new_user, social_id_field, user_info["id"])
            
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            
            # Create default preferences
            await self.user_service.create_default_preferences(new_user.id)
            
            return new_user
            
        except Exception as e:
            await self.db.rollback()
            return None