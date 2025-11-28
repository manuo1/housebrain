from django.core.cache import cache


def set_radiators_to_turn_on_in_cache(radiators_list: list) -> None:
    cache.set("radiators_to_turn_on", radiators_list, timeout=None)


def get_radiators_to_turn_on_in_cache() -> list:
    return cache.get("radiators_to_turn_on", [])
