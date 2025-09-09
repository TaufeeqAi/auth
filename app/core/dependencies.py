# Dependency injection
# backend/app/core/dependencies.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from structlog import get_logger

from ..database.session import get_db
from ..models.user import User
from ..repositories.user_repository import UserRepository
from .security import verify_token
from .exceptions import AuthenticationException

logger = get_logger()
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract and validate user ID from JWT token"""
    token = credentials.credentials
    user_id = verify_token(token, token_type="access")
    
    if user_id is None:
        raise AuthenticationException("Invalid authentication token")
    
    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise AuthenticationException("User not found")
    
    if not user.is_active:
        raise AuthenticationException("Inactive user")
    
    return user


async def get_current_active_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user has manager role"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Manager role required."
        )
    return current_user


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency injection for UserRepository"""
    return UserRepository(db)
