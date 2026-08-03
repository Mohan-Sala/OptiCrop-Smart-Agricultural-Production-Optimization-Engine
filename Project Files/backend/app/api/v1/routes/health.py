from datetime import datetime, timezone
from fastapi import APIRouter, status
from app.core.config import settings
from app.database.connection import check_db_connection
from app.storage.supabase import check_supabase_connection, check_storage_connection
from app.utils.responses import json_response

router = APIRouter()


@router.get("", summary="Extended Health Check")
async def get_health():
    """Returns the API health status along with database, supabase, and storage connectivity."""
    db_ok = await check_db_connection()
    supabase_ok = await check_supabase_connection()
    storage_ok = await check_storage_connection()

    services_status = {
        "database": "connected" if db_ok else "disconnected",
        "supabase": "connected" if supabase_ok else "disconnected",
        "storage": "connected" if storage_ok else "disconnected",
    }

    # If any service check fails, mark status as degraded and return 503 Service Unavailable
    is_healthy = db_ok and supabase_ok and storage_ok
    overall_status = "healthy" if is_healthy else "unhealthy"
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    health_data = {
        "status": overall_status,
        "application_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services_status,
    }

    message = "Service is fully operational" if is_healthy else "One or more dependent services are offline"
    return json_response(
        status_code=status_code,
        success=is_healthy,
        message=message,
        data=health_data,
    )
