from django.core.cache import cache


def get_sensors_data_in_cache():
    return cache.get("sensors_data", {})
