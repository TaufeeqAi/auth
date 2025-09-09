
### backend/app/repositories/device_repository.py
"""Device data access layer"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from datetime import datetime

from ..models.device import Device
from .base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    def __init__(self, db: AsyncSession):
        super().__init__(Device, db)

    async def get_by_device_id(self, user_id: str, device_id: str) -> Optional[Device]:
        """Get device by device ID for specific user"""
        query = select(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_id
        )
        return await self.db.scalar(query)

    async def get_user_devices(self, user_id: str, active_only: bool = True) -> List[Device]:
        """Get all devices for a user"""
        query = select(Device).where(Device.user_id == user_id)
        
        if active_only:
            query = query.where(Device.is_active == True)
            
        query = query.order_by(Device.last_active.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_last_active(self, device_id: str) -> bool:
        """Update device last active timestamp"""
        query = update(Device).where(Device.id == device_id).values(
            last_active=datetime.utcnow()
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def deactivate_device(self, user_id: str, device_id: str) -> bool:
        """Deactivate a device"""
        query = update(Device).where(
            Device.user_id == user_id,
            Device.device_id == device_id
        ).values(is_active=False)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0