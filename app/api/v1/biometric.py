
### backend/app/api/v1/biometric.py
"""Biometric authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.dependencies import get_current_user, get_db
from ...schemas.auth import BiometricSetup
from ...schemas.token import BiometricAuthRequest, TokenResponse
from ...services.implementations.biometric_service import BiometricService
from ...models.user import User

router = APIRouter(prefix="/biometric", tags=["biometric"])


@router.post("/setup")
async def setup_biometric_auth(
    biometric_data: BiometricSetup,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup biometric authentication for user"""
    service = BiometricService(db)
    success = await service.setup_biometric(current_user.id, biometric_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to setup biometric authentication"
        )
    return {"message": "Biometric authentication setup successfully"}


@router.post("/authenticate", response_model=TokenResponse)
async def authenticate_biometric(
    auth_data: BiometricAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate using biometric data"""
    service = BiometricService(db)
    token_response = await service.authenticate_biometric(auth_data)
    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Biometric authentication failed"
        )
    return token_response


@router.get("/challenge/{device_id}")
async def get_biometric_challenge(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get biometric authentication challenge"""
    service = BiometricService(db)
    challenge = await service.generate_challenge(current_user.id, device_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or biometric not setup"
        )
    return {"challenge": challenge}


@router.delete("/disable")
async def disable_biometric_auth(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable biometric authentication"""
    service = BiometricService(db)
    success = await service.disable_biometric(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable biometric authentication"
        )
    return {"message": "Biometric authentication disabled successfully"}
