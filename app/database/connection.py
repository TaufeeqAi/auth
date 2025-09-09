from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql import text
from structlog import get_logger
from ..core.config import settings

logger = get_logger()

# Log the database URL for debugging
logger.info("Attempting to connect to asynchronous database", database_url=settings.DATABASE_URL)

# Create an asynchronous database engine with connection pooling.
# Note the URL uses the 'asyncpg' driver for asynchronous PostgreSQL connections.
async_engine: AsyncEngine = create_async_engine(
    # The URL must be in the format 'postgresql+asyncpg://user:password@host:port/database'
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=settings.is_development,  # Log SQL queries in development
)

# Test the connection at startup
async def test_database_connection() -> None:
    """
    Tests the asynchronous database connection at application startup.
    """
    try:
        # The .begin() method creates a transaction and context manager
        # that handles committing or rolling back the connection.
        async with async_engine.begin() as connection:
            logger.info("Asynchronous database connection successful!")
            # Corrected: using text() to make the query executable
            result = await connection.execute(text("select pg_catalog.version()"))
            logger.info(f"Connected to PostgreSQL version: {result.scalar()}")
    except Exception as e:
        logger.error("Failed to connect to the database", exc_info=e)
        # Re-raise the exception to prevent the application from starting with a bad connection
        raise

# A simple atexit handler to ensure the engine is properly disposed of on shutdown
import atexit
atexit.register(lambda: async_engine.sync_engine.dispose())