from core.utils.date_utils import parse_iso_datetime
from core.utils.temperatures import validate_temperature_value
from sensors.utils.cache_sensors_data import get_sensor_data_in_cache


def get_sensor_temperatures(mac_address: str) -> dict:
    sensor_info = get_sensor_data_in_cache(mac_address)

    try:
        return {
            "temperature": validate_temperature_value(
                sensor_info["measurements"]["temperature"]
            ),
            "dt": parse_iso_datetime(sensor_info["measurements"]["dt"]),
            "previous_temperature": validate_temperature_value(
                sensor_info["previous_measurements"]["temperature"]
            ),
            "previous_dt": parse_iso_datetime(
                sensor_info["previous_measurements"]["dt"]
            ),
        }
    except (TypeError, KeyError):
        return {
            "temperature": None,
            "dt": None,
            "previous_temperature": None,
            "previous_dt": None,
        }
