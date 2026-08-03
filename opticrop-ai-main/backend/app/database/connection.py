import logging
from sqlalchemy import text
from app.database.session import async_session

logger = logging.getLogger("app.database.connection")


async def check_db_connection() -> bool:
    """Verifies connection liveness by executing a simple SELECT 1 query.

    Returns:
        bool: True if connection is responsive, False otherwise.
    """
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            logger.debug("Database liveness check succeeded.")
            return True
    except Exception as e:
        logger.error("Database health check connection failed: %s", str(e))
        return False
