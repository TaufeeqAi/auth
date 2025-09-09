# backend/app/api/v1/auth.py (Updated)

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger
from typing import Annotated
import traceback
import uuid

from app.schemas.token import SocialAuthRequest
from app.services.implementations.social_auth_service import SocialAuthService

from ...database.session import get_db
from ...schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest,
    TokenResponse, PasswordResetRequest
)
from ...schemas.user import UserCreate, UserResponse
from ...schemas.common import APIResponse
from ...services.implementations.jwt_auth_service import JWTAuthService
from ...services.implementations.user_service_impl import UserServiceImpl
from ...core.exceptions import AuthenticationException, ConflictException
from ..deps import get_auth_service, get_user_service

router = APIRouter()
logger = get_logger()


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_service: UserServiceImpl = Depends(get_user_service)
):
    """Register a new user"""
    logger.info("Register request received", email=user_data.email, username=user_data.username)

    try:
        logger.info("Attempting to create user", email=user_data.email)
        user = await user_service.create_user(user_data)

        logger.info("User registered successfully", user_id=user.id, email=user.email, username=user.username)

        return APIResponse(
            success=True,
            message="User registered successfully",
            data={
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            }
        )
    except ConflictException as e:
        logger.error("Registration failed: user already exists", email=user_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Unexpected error during registration",
                     email=user_data.email,
                     error=str(e),
                     traceback=traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: JWTAuthService = Depends(get_auth_service)
):
    """Authenticate user and return tokens"""
    logger.info("Login request received", email=login_data.email)

    user = await auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password
    )

    if not user:
        logger.warning("Login failed: incorrect email or password", email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ensure device_id is present
    device_id = login_data.device_id or str(uuid.uuid4())
    logger.debug("User authenticated successfully, creating tokens", user_id=user.id, device_id=device_id)

    tokens = await auth_service.create_tokens(user, device_id=device_id)
    logger.info("Login successful, tokens created", user_id=user.id, device_id=device_id)

    return LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            avatar_url=user.avatar_url,
            bio=getattr(user, "bio", None),
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: JWTAuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    logger.info("Refresh token request received")
    # TODO: Implement refresh token logic in Phase 2
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token functionality will be implemented in Phase 2"
    )


@router.post("/logout", response_model=APIResponse)
async def logout():
    """Logout user (revoke tokens)"""
    logger.info("Logout request received")
    # TODO: Implement token revocation in Phase 2
    return APIResponse(
        success=True,
        message="Logged out successfully"
    )


@router.post("/social/google", response_model=TokenResponse)
async def google_login(
    auth_data: SocialAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Google OAuth login"""
    if auth_data.provider != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider"
        )

    social_auth_service = SocialAuthService(db)
    token_response = await social_auth_service.authenticate_social(auth_data)

    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed"
        )

    return token_response


@router.post("/social/apple", response_model=TokenResponse)
async def apple_login(
    auth_data: SocialAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Apple OAuth login"""
    if auth_data.provider != "apple":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider"
        )

    social_auth_service = SocialAuthService(db)
    token_response = await social_auth_service.authenticate_social(auth_data)

    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Apple authentication failed"
        )

    return token_response


@router.post("/password-reset-request", response_model=APIResponse)
async def password_reset_request(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    user_service: UserServiceImpl = Depends(get_user_service)
):
    """Request password reset"""
    logger.info("Password reset request received", email=reset_data.email)
    user = await user_service.get_user_by_email(reset_data.email)

    if user:
        # TODO: Implement email sending in Phase 2
        logger.info("User found, password reset link will be sent (feature not yet implemented)", email=reset_data.email)

    # Always return success for security (don't reveal if email exists)
    logger.info("Password reset request processed", email=reset_data.email)

    return APIResponse(
        success=True,
        message="If the email exists, a password reset link has been sent"
    )
