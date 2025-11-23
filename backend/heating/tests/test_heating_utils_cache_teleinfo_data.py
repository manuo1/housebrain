from django.core.cache import cache
from heating.utils.cache_radiators import (
    get_radiators_to_turn_on_in_cache,
    set_radiators_to_turn_on_in_cache,
)

RADIATORS = [{"id": 1}, {"id": 2}]


def test_set_radiators_to_turn_on_in_cache():
    set_radiators_to_turn_on_in_cache(RADIATORS)
    assert cache.get("radiators_to_turn_on") == RADIATORS


def test_get_radiators_to_turn_on_in_cache():
    set_radiators_to_turn_on_in_cache(RADIATORS)
    assert get_radiators_to_turn_on_in_cache() == RADIATORS
