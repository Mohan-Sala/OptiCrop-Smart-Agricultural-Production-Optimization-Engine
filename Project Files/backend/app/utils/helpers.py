from datetime import datetime, timezone


def get_current_utc_time() -> datetime:
    """Returns the current date and time in UTC timezone."""
    return datetime.now(timezone.utc)


def format_iso_timestamp(dt: datetime) -> str:
    """Formats a datetime object to an ISO format string."""
    return dt.isoformat()
