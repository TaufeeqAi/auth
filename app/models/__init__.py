# backend/app/models/__init__.py
# Import all model modules so the declarative registry registers each mapper
from .base import Base, BaseModel

# Import every model module here. Add more imports as you add model files.
# The names should match your actual filenames.
from .user import User
from .user_session import UserSession
from .refresh_token import RefreshToken
from .user_preferences import UserPreferences
from .device import Device
# ... import other models used in your project ...

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "UserSession",
    "RefreshToken",
    "UserPreferences",
    "Device",
]
