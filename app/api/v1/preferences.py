### backend/app/api/v1/preferences.py
"""User preferences endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.dependencies import get_current_user, get_db
from ...schemas.preferences import UserPreferencesUpdate, UserPreferencesResponse
from ...services.implementations.preferences_service import PreferencesService
from ...models.user import User

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences"""
    service = PreferencesService(db)
    preferences = await service.get_user_preferences(current_user.id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    return preferences


@router.put("/", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    service = PreferencesService(db)
    preferences = await service.update_user_preferences(
        current_user.id, 
        preferences_data
    )
    return preferences


@router.post("/theme/preview")
async def preview_theme(
    theme_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Preview theme settings without saving"""
    # Validate theme data
    allowed_keys = {"theme_mode", "primary_color", "accent_color"}
    if not set(theme_data.keys()).issubset(allowed_keys):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid theme data keys"
        )
    
    return {"message": "Theme preview data validated", "theme": theme_data}
