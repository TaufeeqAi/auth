# User service interface
# backend/app/services/interfaces/user_service.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ...models.user import User
from ...schemas.user import UserCreate, UserUpdate


class UserServiceInterface(ABC):
    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        pass