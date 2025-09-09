from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from structlog import get_logger
import traceback

from ..interfaces.user_service import UserServiceInterface
from ...models.user import User
from ...schemas.user import UserCreate, UserUpdate
from ...core.exceptions import ConflictException, NotFoundException
from ...core.security import get_password_hash

logger = get_logger()

class UserServiceImpl(UserServiceInterface):
    """
    Service implementation for managing users.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        """
        logger.info("Attempting to create user in service", email=user_data.email, username=user_data.username)
        
        try:
            logger.info("Checking if user already exists by email", email=user_data.email)
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning("User with this email already exists", email=user_data.email)
                raise ConflictException("User with this email already exists")
            
            logger.info("Checking if user already exists by username", username=user_data.username)
            existing_username = await self.get_user_by_username(user_data.username)
            if existing_username:
                logger.warning("User with this username already exists", username=user_data.username)
                raise ConflictException("User with this username already exists")
            
            logger.info("Hashing user password", email=user_data.email)
            # Hash the user's password
            hashed_password = get_password_hash(user_data.password)

            logger.info("Creating user instance", email=user_data.email)
            # Create user instance
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                password_hash=hashed_password,
                full_name=user_data.full_name,
                organization_name=user_data.organization_name,
                department_id=user_data.department_id,
                phone_number=user_data.phone_number,
                role=user_data.role,
                is_active=True,
                is_verified=False
            )
            
            logger.info("Adding user to database", email=user_data.email)
            # Add and commit to the database
            self.db.add(db_user)
            
            logger.info("Committing user to database", email=user_data.email)
            await self.db.commit()
            
            logger.info("Refreshing user from database", email=user_data.email)
            await self.db.refresh(db_user)
            
            logger.info("User created successfully", user_id=db_user.id, email=db_user.email, username=db_user.username)
            return db_user
            
        except ConflictException:
            logger.warning("Conflict exception caught", email=user_data.email)
            raise
        except SQLAlchemyError as e:
            logger.error("Database error during user creation", 
                        email=user_data.email, 
                        error=str(e),
                        traceback=traceback.format_exc())
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Unexpected error during user creation", 
                        email=user_data.email, 
                        error=str(e),
                        traceback=traceback.format_exc())
            await self.db.rollback()
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            update_dict = user_data.model_dump(exclude_unset=True)
            if not update_dict:
                return user
            
            for key, value in update_dict.items():
                setattr(user, key, value)
            
            await self.db.commit()
            await self.db.refresh(user)

            logger.info("User updated successfully", user_id=user_id)
            return user
            
        except NotFoundException:
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error("Database error during user update", user_id=user_id, error=str(e))
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user (soft delete by deactivating).
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            await self.db.commit()
            await self.db.refresh(user)

            logger.info("User deactivated", user_id=user_id)
            return True
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error("Database error during user deletion", user_id=user_id, error=str(e))
            return False
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """
        Get list of users with pagination and filtering.
        """
        query = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        
        # This is a simplified filter, expand as needed
        if filters and "email" in filters:
            query = query.where(User.email.ilike(f"%{filters['email']}%"))
            
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create_default_preferences(self, user_id: str) -> None:
        """
        Create default preferences for a new user.
        """
        try:
            from ...models.user_preferences import UserPreferences
            
            # Check if preferences already exist
            from sqlalchemy import select
            query = select(UserPreferences).where(UserPreferences.user_id == user_id)
            result = await self.db.execute(query)
            existing_prefs = result.scalar_one_or_none()
            
            if not existing_prefs:
                # Create default preferences
                default_prefs = UserPreferences(
                    user_id=user_id,
                    language="en",
                    timezone="UTC"
                )
                self.db.add(default_prefs)
                await self.db.commit()
                
        except Exception as e:
            await self.db.rollback()
            logger.error("Error creating default preferences", user_id=user_id, error=str(e))
