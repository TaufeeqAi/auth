# Base Pydantic schema
# backend/app/schemas/base.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseSchema):
    created_at: datetime
    updated_at: Optional[datetime] = None


class APIResponse(BaseSchema):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[dict] = None
    error_code: Optional[str] = None


class PaginationParams(BaseSchema):
    page: int = 1
    limit: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseSchema):
    items: list
    total: int
    page: int
    limit: int
    pages: int
