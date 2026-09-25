import logging
from app.database.mongodb import check_mongodb_connection

logger = logging.getLogger("app.database.connection")


async def check_db_connection() -> bool:
    """Verifies connection liveness by executing a MongoDB admin ping.

    Returns:
        bool: True if connection is responsive, False otherwise.
    """
    return await check_mongodb_connection()
