from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi.util import get_remote_address
from structlog import get_logger
import traceback

from ..database.session import get_db
from ..models.user import User
from ..services.implementations.user_service_impl import UserServiceImpl
from ..services.implementations.jwt_auth_service import JWTAuthService
from ..core.security import verify_token
from ..core.exceptions import AuthenticationException, RateLimitException

logger = get_logger()
security = HTTPBearer()

async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """Extract and validate user ID from JWT token"""
    logger.info("Extracting user ID from JWT token")
    token = credentials.credentials
    user_id = verify_token(token, token_type="access")
    
    if user_id is None:
        logger.warning("Invalid authentication token provided")
        raise AuthenticationException("Invalid authentication token")
    
    logger.info("User ID extracted from token", user_id=user_id)
    return user_id

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Annotated[AsyncSession, Depends(get_db)] = None
) -> User:
    """Get current authenticated user"""
    logger.info("Getting current user", user_id=user_id)
    user_service = UserServiceImpl(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.warning("User not found", user_id=user_id)
        raise AuthenticationException("User not found")
    
    if not user.is_active:
        logger.warning("Inactive user", user_id=user_id)
        raise AuthenticationException("Inactive user")
    
    logger.info("Current user retrieved", user_id=user.id, email=user.email)
    return user


async def get_current_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user has manager role"""
    logger.info("Checking if user has manager role", user_id=current_user.id, role=current_user.role)
    if current_user.role.value != "manager":
        logger.warning("Manager role required", user_id=current_user.id, role=current_user.role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager role required"
        )
    logger.info("User has manager role", user_id=current_user.id)
    return current_user

async def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserServiceImpl:
    """Dependency injection for UserService"""
    logger.info("Creating UserService instance")
    try:
        service = UserServiceImpl(db)
        logger.info("UserService instance created successfully")
        return service
    except Exception as e:
        logger.error("Error creating UserService instance", 
                    error=str(e),
                    traceback=traceback.format_exc())
        raise

async def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> JWTAuthService:
    """Dependency injection for AuthService"""
    logger.info("Creating AuthService instance")
    try:
        service = JWTAuthService(db)
        logger.info("AuthService instance created successfully")
        return service
    except Exception as e:
        logger.error("Error creating AuthService instance", 
                    error=str(e),
                    traceback=traceback.format_exc())
        raise
