# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from sqlalchemy import Enum as SQLEnum
from .base import BaseModel

class UserRole(enum.Enum):
    ATTENDEE = "attendee"
    MANAGER = "manager"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=True, unique=True, index=True)
    full_name = Column(String(255), nullable=True)

    # Organization information
    organization_name = Column(String(255), nullable=True)
    department_id = Column(String(100), nullable=True)

    # Authentication
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(SQLEnum(UserRole, name="userrole"), default=UserRole.ATTENDEE, nullable=False)

    # Social login
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    apple_id = Column(String(255), nullable=True, unique=True, index=True)

    # Biometric authentication
    biometric_enabled = Column(Boolean, default=False, nullable=False)
    biometric_public_key = Column(Text, nullable=True)

    # Profile
    avatar_url = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True, index=True)

    # NOTE: Do NOT re-declare created_at / updated_at here — inherited from BaseModel

    # Relationships
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    devices = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    preferences = relationship(
        "UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # Fix for your mapper errors: expose sessions relationship (other models were expecting it)
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
