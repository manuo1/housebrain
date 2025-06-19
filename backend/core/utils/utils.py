from core.constants import TerminalColor, DEFAULT_VOLTAGE
from datetime import datetime


def colored_text(text: str, color: TerminalColor) -> str:
    """Add color to terminal output."""
    return f"\033[{color.value}m{text}\033[0m"


def watt_to_ampere(watt: int | float) -> float:
    """Convert intensity to power"""
    if not isinstance(watt, (int, float)):
        return None
    return watt / DEFAULT_VOLTAGE


def ampere_to_watt(intensity: int | float) -> float:
    """Convert power to intensity"""
    if not isinstance(intensity, (int, float)):
        return None
    return intensity * DEFAULT_VOLTAGE


def is_new_hour(old_datetime: datetime, new_datetime: datetime) -> bool:
    """Check if the time of new_datetime is newer than old_datetime"""
    if not all(isinstance(var, datetime) for var in (old_datetime, new_datetime)):
        return False
    rounded_old_datetime = old_datetime.replace(minute=0, second=0, microsecond=0)
    rounded_new_datetime = new_datetime.replace(minute=0, second=0, microsecond=0)
    return rounded_new_datetime > rounded_old_datetime


def decode_byte(byte_data: bytes) -> str | None:
    try:
        return byte_data.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None


def wh_to_watt(wh: float, duration_minutes: float) -> float:
    """Convert watt hour to watt"""
    if not isinstance(wh, (int, float)):
        return None
    if not duration_minutes:
        return None
    duration_hours = duration_minutes / 60
    return wh / duration_hours
