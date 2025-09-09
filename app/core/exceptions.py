# Custom exception classes
# backend/app/core/exceptions.py
from typing import Any, Dict, Optional
from fastapi import HTTPException


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Validation error", 
        error_code: str = "VALIDATION_ERROR"
    ):
        super().__init__(
            status_code=422, 
            detail=detail, 
            error_code=error_code
        )


class AuthenticationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Authentication failed", 
        error_code: str = "AUTHENTICATION_ERROR"
    ):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Not enough permissions", 
        error_code: str = "AUTHORIZATION_ERROR"
    ):
        super().__init__(
            status_code=403, 
            detail=detail, 
            error_code=error_code
        )


class NotFoundException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Resource not found", 
        error_code: str = "NOT_FOUND"
    ):
        super().__init__(
            status_code=404, 
            detail=detail, 
            error_code=error_code
        )


class ConflictException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Resource conflict", 
        error_code: str = "CONFLICT"
    ):
        super().__init__(
            status_code=409, 
            detail=detail, 
            error_code=error_code
        )


class RateLimitException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Rate limit exceeded", 
        error_code: str = "RATE_LIMIT_EXCEEDED"
    ):
        super().__init__(
            status_code=429, 
            detail=detail, 
            error_code=error_code
        )