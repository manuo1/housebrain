from datetime import datetime, timedelta


def is_delta_within_one_minute(dt1: datetime, dt2: datetime) -> bool:
    """Check if the difference between two datetime objects is less than or equal to 1 minute."""
    return abs(dt1 - dt2) <= timedelta(minutes=1)


def parse_iso_datetime(dt_str: str) -> datetime | None:
    """Convert an ISO 8601 datetime string (e.g., "2025-10-15T10:55:53.438Z") to a datetime object."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None
