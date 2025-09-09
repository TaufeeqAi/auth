
### backend/app/services/implementations/biometric_service.py
"""Biometric verification service"""

import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from ...models.user import User
from ...models.device import Device
from ...schemas.auth import BiometricSetup
from ...schemas.token import BiometricAuthRequest, TokenResponse
from .jwt_auth_service import JWTAuthService


class BiometricService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = JWTAuthService(db)

    async def setup_biometric(self, user_id: str, biometric_data: BiometricSetup) -> bool:
        """Setup biometric authentication for user"""
        try:
            # Verify device belongs to user
            device_query = select(Device).where(
                Device.user_id == user_id,
                Device.device_id == biometric_data.device_id,
                Device.is_active == True
            )
            device = await self.db.scalar(device_query)
            
            if not device:
                return False
                
            # Update user with biometric info
            user_update = update(User).where(User.id == user_id).values(
                biometric_enabled=True,
                biometric_public_key=biometric_data.public_key
            )
            await self.db.execute(user_update)
            
            # Update device with biometric capability
            device_update = update(Device).where(
                Device.user_id == user_id,
                Device.device_id == biometric_data.device_id
            ).values(
                supports_biometric=True,
                biometric_type=biometric_data.biometric_type
            )
            await self.db.execute(device_update)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            return False

    async def authenticate_biometric(self, auth_data: BiometricAuthRequest) -> Optional[TokenResponse]:
        """Authenticate user using biometric data"""
        try:
            # Get user and device
            user_query = select(User).where(
                User.id == auth_data.user_id,
                User.biometric_enabled == True,
                User.is_active == True
            )
            user = await self.db.scalar(user_query)
            
            if not user:
                return None
                
            device_query = select(Device).where(
                Device.user_id == auth_data.user_id,
                Device.device_id == auth_data.device_id,
                Device.supports_biometric == True,
                Device.is_active == True
            )
            device = await self.db.scalar(device_query)
            
            if not device:
                return None
                
            # Verify biometric signature
            if not self._verify_biometric_signature(
                user.biometric_public_key,
                auth_data.biometric_signature,
                auth_data.challenge
            ):
                return None
                
            # Generate tokens
            token_response = await self.auth_service.create_tokens(user, auth_data.device_id)
            
            # Update last login
            await self.db.execute(
                update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
            )
            await self.db.execute(
                update(Device).where(
                    Device.user_id == user.id,
                    Device.device_id == auth_data.device_id
                ).values(last_active=datetime.utcnow())
            )
            
            await self.db.commit()
            return token_response
            
        except Exception as e:
            await self.db.rollback()
            return None

    async def generate_challenge(self, user_id: str, device_id: str) -> Optional[str]:
        """Generate biometric authentication challenge"""
        # Verify device supports biometric
        device_query = select(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_id,
            Device.supports_biometric == True,
            Device.is_active == True
        )
        device = await self.db.scalar(device_query)
        
        if not device:
            return None
            
        # Generate random challenge
        challenge = secrets.token_urlsafe(32)
        return challenge

    async def disable_biometric(self, user_id: str) -> bool:
        """Disable biometric authentication for user"""
        try:
            # Update user
            user_update = update(User).where(User.id == user_id).values(
                biometric_enabled=False,
                biometric_public_key=None
            )
            await self.db.execute(user_update)
            
            # Update all user devices
            device_update = update(Device).where(Device.user_id == user_id).values(
                supports_biometric=False,
                biometric_type=None
            )
            await self.db.execute(device_update)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            return False

    def _verify_biometric_signature(self, public_key: str, signature: str, challenge: str) -> bool:
        """Verify biometric signature (simplified implementation)"""
        # In a real implementation, this would use proper cryptographic verification
        # This is a simplified version for demonstration
        try:
            # Decode the signature and public key
            sig_bytes = base64.b64decode(signature)
            key_bytes = base64.b64decode(public_key)
            
            # Create expected hash
            expected = hashlib.sha256(f"{challenge}{key_bytes.hex()}".encode()).digest()
            
            # Simple comparison (in production, use proper cryptographic verification)
            return sig_bytes == expected
            
        except Exception:
            return False
