from core.utils.env_utils import environment_is_development
from django.core.cache import cache
from mock_data.sensors import MOCKED_SENSORS_DATA


def get_sensors_data_in_cache():
    if environment_is_development():
        return MOCKED_SENSORS_DATA
    return cache.get("sensors_data", {})
