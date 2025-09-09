
### backend/app/schemas/token.py
"""Token response schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    device_id: str


class BiometricAuthRequest(BaseModel):
    user_id: str
    device_id: str
    biometric_signature: str
    challenge: str


class SocialAuthRequest(BaseModel):
    provider: str = Field(..., pattern="^(google|apple)$")
    access_token: str
    device_info: Optional[dict] = None