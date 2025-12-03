from core.utils.env_utils import environment_is_development
from django.core.cache import cache
from mock_data.sensors import MOCKED_SENSORS_DATA


def get_sensors_data_in_cache():
    if environment_is_development():
        return MOCKED_SENSORS_DATA
    return cache.get("sensors_data", {})


def get_sensor_data_in_cache(mac_address: str) -> object | None:
    if not isinstance(mac_address, str):
        return
    return get_sensors_data_in_cache().get(mac_address)
