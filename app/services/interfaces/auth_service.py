# Auth service interface
# backend/app/services/interfaces/auth_service.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ...models.user import User
from ...schemas.auth import LoginResponse, TokenResponse


class AuthServiceInterface(ABC):
    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def create_user_tokens(self, user: User) -> TokenResponse:
        pass
    
    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> Optional[TokenResponse]:
        pass
    
    @abstractmethod
    async def revoke_token(self, user_id: str, refresh_token: str) -> bool:
        pass
