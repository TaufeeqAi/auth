from pydantic import BaseModel
from typing import Any, Optional, Dict, List, Generic, TypeVar


# A TypeVar to make the APIResponse generic
T = TypeVar("T")


class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    success: bool = False
    message: str = "Validation error"
    error_code: str = "VALIDATION_ERROR"
    errors: List[Dict[str, Any]]


class APIResponse(BaseModel, Generic[T]):
    """
    A generic Pydantic model for standardizing API responses.

    This model provides a consistent structure for success/failure messages
    and data payloads across the API.
    """
    success: bool
    message: str
    data: T | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """
    A generic Pydantic model for paginated API responses.

    This model provides a consistent structure for paginated data,
    including metadata for a cursor-based approach.
    """
    data: List[T]
    page_size: int
    next_cursor: Optional[str] = None
    has_more: bool
