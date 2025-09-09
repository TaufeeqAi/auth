# User DTOs
# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from ..models.user import UserRole
from .base import BaseSchema, TimestampMixin


class UserBase(BaseSchema):
    email: EmailStr
    username: str
    full_name: str
    organization_name: Optional[str] = None
    department_id: Optional[str] = None
    role: UserRole = UserRole.ATTENDEE
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str
    confirm_password: str
    phone_number: Optional[str] = None
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        return v


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    organization_name: Optional[str] = None
    department_id: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None


class UserPasswordUpdate(BaseSchema):
    current_password: str
    new_password: str
    confirm_new_password: str
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


class UserInDB(UserBase, TimestampMixin):
    id: str
    is_active: bool
    is_verified: bool


class UserResponse(BaseSchema):
    id: str
    email: EmailStr
    username: str
    full_name: str
    organization_name: Optional[str] = None
    department_id: Optional[str] = None
    role: UserRole
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: Optional[str] = None
