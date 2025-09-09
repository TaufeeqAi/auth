
### backend/app/services/implementations/device_service.py
"""Device management service"""

import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional

from ...models.device import Device, DeviceType
from ...schemas.device import DeviceRegister, DeviceUpdate, DeviceResponse
from ...utils.push_notifications import FCMService


class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fcm_service = FCMService()

    async def register_device(self, user_id: str, device_data: DeviceRegister) -> DeviceResponse:
        """Register a new device for user"""
        # Check if device already exists
        existing_query = select(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_data.device_id
        )
        existing_device = await self.db.scalar(existing_query)
        
        if existing_device:
            # Update existing device
            for field, value in device_data.dict(exclude_unset=True).items():
                if field == "metadata" and value:
                    value = json.dumps(value)
                setattr(existing_device, field, value)
            
            existing_device.is_active = True
            existing_device.last_active = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(existing_device)
            return DeviceResponse.from_orm(existing_device)
        
        # Create new device
        device = Device(
            user_id=user_id,
            device_id=device_data.device_id,
            device_name=device_data.device_name,
            device_type=DeviceType(device_data.device_type.value),
            platform_version=device_data.platform_version,
            app_version=device_data.app_version,
            fcm_token=device_data.fcm_token,
            apns_token=device_data.apns_token,
            supports_biometric=device_data.supports_biometric,
            biometric_type=device_data.biometric_type,
            metadata=json.dumps(device_data.metadata) if device_data.metadata else None,
            last_active=datetime.utcnow()
        )
        
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        
        return DeviceResponse.from_orm(device)

    async def get_user_devices(self, user_id: str) -> List[DeviceResponse]:
        """Get all user devices"""
        query = select(Device).where(
            Device.user_id == user_id,
            Device.is_active == True
        ).order_by(Device.last_active.desc())
        
        result = await self.db.execute(query)
        devices = result.scalars().all()
        
        return [DeviceResponse.from_orm(device) for device in devices]

    async def update_device(self, user_id: str, device_id: str, device_data: DeviceUpdate) -> Optional[DeviceResponse]:
        """Update device information"""
        query = select(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_id,
            Device.is_active == True
        )
        device = await self.db.scalar(query)
        
        if not device:
            return None
            
        # Update device fields
        for field, value in device_data.dict(exclude_unset=True).items():
            if field == "metadata" and value:
                value = json.dumps(value)
            setattr(device, field, value)
        
        device.last_active = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(device)
        
        return DeviceResponse.from_orm(device)

    async def deactivate_device(self, user_id: str, device_id: str) -> bool:
        """Deactivate a device"""
        query = select(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_id
        )
        device = await self.db.scalar(query)
        
        if not device:
            return False
            
        device.is_active = False
        await self.db.commit()
        
        return True

    async def send_test_notification(self, user_id: str, device_id: str) -> bool:
        """Send test push notification to device"""
        query = select(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_id,
            Device.is_active == True
        )
        device = await self.db.scalar(query)
        
        if not device:
            return False
            
        # Send FCM notification if token exists
        if device.fcm_token:
            success = await self.fcm_service.send_notification(
                device.fcm_token,
                title="Test Notification",
                body="Your device is successfully connected!",
                data={"type": "test", "device_id": device_id}
            )
            return success
            
        return False
