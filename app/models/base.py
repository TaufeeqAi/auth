# backend/app/models/base.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Use orm.declarative_base for clarity with modern SQLAlchemy
Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Use server_default for created_at to let DB set the value consistently
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Let the DB handle updated_at with onupdate when you issue updates
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
