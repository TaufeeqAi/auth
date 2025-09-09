
### backend/app/schemas/device.py
"""Device registration DTOs"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DeviceTypeSchema(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class DeviceRegister(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=255)
    device_name: Optional[str] = Field(None, max_length=255)
    device_type: DeviceTypeSchema
    platform_version: Optional[str] = Field(None, max_length=100)
    app_version: Optional[str] = Field(None, max_length=50)
    fcm_token: Optional[str] = None
    apns_token: Optional[str] = None
    supports_biometric: bool = False
    biometric_type: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = Field(None, max_length=255)
    fcm_token: Optional[str] = None
    apns_token: Optional[str] = None
    supports_biometric: Optional[bool] = None
    biometric_type: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None


class DeviceResponse(BaseModel):
    id: str
    device_id: str
    device_name: Optional[str]
    device_type: DeviceTypeSchema
    platform_version: Optional[str]
    app_version: Optional[str]
    supports_biometric: bool
    biometric_type: Optional[str]
    is_active: bool
    last_active: Optional[datetime]
    registered_at: datetime

    class Config:
        from_attributes = True