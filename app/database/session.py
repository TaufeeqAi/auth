# backend/app/database/session.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from structlog import get_logger
import traceback
from .connection import async_engine

logger = get_logger()

# Create an async session maker.
# The async_sessionmaker is used to create a new AsyncSession instance.
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an asynchronous database session.
    A new session is created for each request and automatically closed after the request
    using the 'async with' context manager.
    """
    logger.info("Creating new database session")
    db = AsyncSessionLocal()
    try:
        logger.debug("Asynchronous database session created")
        yield db
    except SQLAlchemyError as e:
        logger.error("Database session error", 
                    error=str(e),
                    traceback=traceback.format_exc())
        # Rollback the session in case of an error
        await db.rollback()
        raise
    except Exception as e:
        logger.error("Unexpected error in database session", 
                    error=str(e),
                    traceback=traceback.format_exc())
        # Rollback the session in case of an error
        await db.rollback()
        raise
    finally:
        # Close the session, which is important for resource management
        await db.close()
        logger.debug("Asynchronous database session closed")
