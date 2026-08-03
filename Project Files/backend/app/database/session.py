import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

logger = logging.getLogger("app.database.session")

# Ensure DATABASE_URL is converted to asyncpg dialect if needed
database_url = settings.DATABASE_URL
if database_url:
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    # Fallback to shared in-memory sqlite for testing/local development if not configured
    database_url = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"
    logger.warning("DATABASE_URL is not set. Falling back to shared in-memory SQLite for database layer.")

# Create the async engine with connection pooling parameters suitable for enterprise loads
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # checks connection liveness before checking it out
    pool_recycle=1800,   # recycles connections older than 30 minutes
    pool_size=10,
    max_overflow=20,
)

# Async session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection provider yielding an asynchronous database session.

    Guarantees clean session teardown and rollbacks on unhandled exceptions.
    """
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session transaction failed; rolling back. Error: %s", str(e))
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Database session closed.")
