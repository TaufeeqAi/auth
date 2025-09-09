from typing import Optional, Dict, Any, List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from passlib.context import CryptContext

from ..models.user import User, UserRole
from ..core.security import get_password_hash, verify_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.
        """
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get a user by their email or username."""
        result = await self.db.execute(
            select(User).where(
                or_(User.email == identifier, User.username == identifier)
            )
        )
        return result.scalars().first()
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user record with a hashed password."""
        try:
            if "password" in user_data:
                user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            
            db_user = User(**user_data)
            self.db.add(db_user)
            await self.db.flush()
            await self.db.refresh(db_user)
            return db_user
        except SQLAlchemyError:
            await self.db.rollback()
            raise
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with their email and password."""
        user = await self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_password(self, user: User, new_password: str) -> User:
        """Update a user's password."""
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_managers(self) -> List[User]:
        """Get a list of active users with the manager role."""
        result = await self.db.execute(
            select(User).where(
                User.role == UserRole.MANAGER,
                User.is_active == True
            )
        )
        return list(result.scalars().all())
    
    async def activate_user(self, user: User) -> User:
        """Activate and verify a user."""
        user.is_active = True
        user.is_verified = True
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def deactivate_user(self, user: User) -> User:
        """Deactivate a user."""
        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        return user
