### backend/app/api/v1/router.py (Enhanced)
"""Enhanced main API router with new endpoints"""

"""Enhanced main API router with new endpoints"""

from fastapi import APIRouter
from .auth import router as auth_router
from .preferences import router as preferences_router
from .devices import router as devices_router
from .biometric import router as biometric_router

api_router = APIRouter()

# Include all routers with their respective prefixes for proper pathing
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(preferences_router, prefix="/preferences", tags=["Preferences"])
api_router.include_router(devices_router, prefix="/devices", tags=["Devices"])
api_router.include_router(biometric_router, prefix="/biometric", tags=["Biometric"])
