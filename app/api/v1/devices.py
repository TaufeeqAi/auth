
### backend/app/api/v1/devices.py
"""Device management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.dependencies import get_current_user, get_db
from ...schemas.device import DeviceRegister, DeviceUpdate, DeviceResponse
from ...services.implementations.device_service import DeviceService
from ...models.user import User

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceResponse)
async def register_device(
    device_data: DeviceRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register a new device"""
    service = DeviceService(db)
    device = await service.register_device(current_user.id, device_data)
    return device


@router.get("/", response_model=List[DeviceResponse])
async def get_user_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all user devices"""
    service = DeviceService(db)
    devices = await service.get_user_devices(current_user.id)
    return devices


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update device information"""
    service = DeviceService(db)
    device = await service.update_device(current_user.id, device_id, device_data)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


@router.delete("/{device_id}")
async def deactivate_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a device"""
    service = DeviceService(db)
    success = await service.deactivate_device(current_user.id, device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return {"message": "Device deactivated successfully"}


@router.post("/{device_id}/test-notification")
async def test_notification(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send test push notification to device"""
    service = DeviceService(db)
    success = await service.send_test_notification(current_user.id, device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or notification failed"
        )
    return {"message": "Test notification sent successfully"}