# backend/app/schemas/auth.py (Enhanced, Updated)
"""Enhanced authentication schemas"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from ..models.user import UserRole
from .user import UserResponse
import re


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[str] = None  
    remember_me: bool = False


class LoginRequest(UserLogin):
    pass


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    device_id: Optional[str] = None  # <-- optional for safety


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str


class BiometricSetup(BaseModel):
    device_id: Optional[str] = None  # <-- optional for setup
    biometric_type: str
    public_key: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetRequest(PasswordReset):
    pass


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
