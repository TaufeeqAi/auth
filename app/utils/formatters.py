# Response formatting
# backend/app/utils/formatters.py
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..schemas.common import APIResponse, PaginatedResponse


def format_api_response(
    success: bool = True,
    message: str = "Operation successful",
    data: Optional[Any] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """Format standard API response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if error_code:
        response["error_code"] = error_code
    
    return response


def format_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    limit: int
) -> Dict[str, Any]:
    """Format paginated response"""
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    }


def format_user_response(user: Any) -> Dict[str, Any]:
    """Format user data for API response"""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }