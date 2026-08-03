import logging
from typing import Optional
import httpx
import anyio
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("app.storage.supabase")

# Initialize the global Supabase client (if credentials exist)
supabase_client: Optional[Client] = None
if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
    try:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        logger.info("Supabase client successfully initialized.")
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", str(e))
else:
    logger.warning("Supabase URL or Anon Key is missing. Storage client will not be initialized.")

# Export configured buckets
BUCKETS = {
    "datasets": "datasets",
    "trained_models": "trained-models",
    "plots": "plots",
    "exports": "exports",
}


def get_storage_client():
    """Exposes the Supabase Storage client."""
    if not supabase_client:
        raise ValueError("Supabase client is not initialized.")
    return supabase_client.storage


async def check_supabase_connection() -> bool:
    """Checks the REST API connectivity to Supabase.

    Returns:
        bool: True if responsive, False otherwise.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        logger.warning("Supabase health check bypassed due to missing credentials.")
        return False

    try:
        async with httpx.AsyncClient() as client:
            # Ping Supabase REST API root endpoint
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/",
                headers={"apikey": settings.SUPABASE_ANON_KEY},
                timeout=5.0,
            )
            is_healthy = response.status_code in (200, 401)  # 401 is okay as it confirms the api responds
            logger.debug("Supabase connectivity health status: %s", is_healthy)
            return is_healthy
    except Exception as e:
        logger.error("Supabase REST connection health check failed: %s", str(e))
        return False


async def check_storage_connection() -> bool:
    """Verifies that the Supabase storage bucket configurations are reachable.

    Returns:
        bool: True if storage API responds successfully, False otherwise.
    """
    if not supabase_client or not settings.STORAGE_BUCKET:
        logger.warning("Supabase Storage health check bypassed due to missing client configuration.")
        return False

    try:
        # Wrap the synchronous SDK storage metadata check inside an async thread pool
        def verify_bucket_access():
            # Tries to retrieve info on the configured bucket
            supabase_client.storage.get_bucket(settings.STORAGE_BUCKET)

        await anyio.to_thread.run_sync(verify_bucket_access)
        logger.debug("Supabase Storage bucket health check succeeded.")
        return True
    except Exception as e:
        logger.error("Supabase Storage connection health check failed: %s", str(e))
        return False
