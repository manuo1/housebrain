from core.constants import DEFAULT_VOLTAGE
from core.utils.date_utils import is_delta_within_five_seconds, parse_iso_datetime
from core.utils.env_utils import environment_is_development
from django.core.cache import cache
from django.utils import timezone
from mock_data.teleinfo import MOCKED_TELEINFO_DATA


def get_teleinfo_data_in_cache() -> dict:
    if environment_is_development():
        return MOCKED_TELEINFO_DATA
    return cache.get("teleinfo_data", {"last_read": None})


def get_teleinfo_data_in_cache_if_up_to_date() -> dict | None:
    data = get_teleinfo_data_in_cache()
    if environment_is_development():
        MOCKED_TELEINFO_DATA["last_read"] = timezone.now().isoformat()
    last_read = parse_iso_datetime(data.get("last_read"))
    if last_read and is_delta_within_five_seconds(last_read, timezone.now()):
        return data


def set_teleinfo_data_in_cache(data: dict) -> None:
    cache.set("teleinfo_data", data, timeout=None)


def get_instant_available_power() -> int:
    teleinfo_data = get_teleinfo_data_in_cache_if_up_to_date()

    try:
        max_available_ampere = int(teleinfo_data.get("ISOUSC"))
        used_ampere = int(teleinfo_data.get("IINST"))
    except (TypeError, ValueError):
        return None

    if used_ampere >= max_available_ampere:
        return 0

    return int((max_available_ampere - used_ampere) * DEFAULT_VOLTAGE)
