from django.core.cache import cache


def set_water_heaters_to_turn_on_in_cache(water_heaters_list: list) -> None:
    cache.set("water_heaters_to_turn_on", water_heaters_list, timeout=None)


def get_water_heaters_to_turn_on_in_cache() -> list:
    return cache.get("water_heaters_to_turn_on", [])
