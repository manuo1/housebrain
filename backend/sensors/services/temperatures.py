from core.utils.date_utils import (
    is_delta_within_one_minute,
    is_delta_within_two_minute,
    parse_iso_datetime,
)
from core.utils.temperatures import validate_temperature_value
from django.utils import timezone
from sensors.utils.cache_sensors_data import get_sensor_data_in_cache


def get_sensor_temperatures(mac_address: str) -> tuple:
    sensor_info = get_sensor_data_in_cache(mac_address)
    now = timezone.localtime(timezone.now())
    current, previous = None, None
    try:
        dt = parse_iso_datetime(sensor_info["measurements"]["dt"])
        temperature_is_recent = is_delta_within_one_minute(dt, now)
        if temperature_is_recent:
            current = validate_temperature_value(
                sensor_info["measurements"]["temperature"]
            )
    except (TypeError, KeyError):
        pass
    try:
        previous_dt = parse_iso_datetime(sensor_info["previous_measurements"]["dt"])
        temperature_is_recent = is_delta_within_two_minute(previous_dt, now)
        if temperature_is_recent:
            previous = validate_temperature_value(
                sensor_info["previous_measurements"]["temperature"]
            )
    except (TypeError, KeyError):
        pass

    return current, previous
