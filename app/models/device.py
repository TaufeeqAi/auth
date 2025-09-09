### backend/app/models/device.py
"""Device registration for push notifications"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from .base import BaseModel


class DeviceType(enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class Device(BaseModel):
    __tablename__ = "devices"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(String(255), nullable=False)  # Unique device identifier
    device_name = Column(String(255), nullable=True)
    device_type = Column(Enum(DeviceType), nullable=False)
    platform_version = Column(String(100), nullable=True)
    app_version = Column(String(50), nullable=True)
    
    # Push notification tokens
    fcm_token = Column(Text, nullable=True)
    apns_token = Column(Text, nullable=True)
    
    # Biometric capability
    supports_biometric = Column(Boolean, default=False)
    biometric_type = Column(String(50), nullable=True)  # fingerprint, face_id, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    last_active = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional device info (JSON string)
    device_metadata = Column(Text, nullable=True, name="metadata")
    
    # Relationships
    user = relationship("User", back_populates="devices")
