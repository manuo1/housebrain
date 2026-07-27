from unittest.mock import patch

import pytest

from mock_data.sensors import MOCKED_SENSORS_DATA
from sensors.utils.cache_sensors_data import (
    get_sensor_data_in_cache,
    get_sensors_data_in_cache,
)


class TestGetSensorsDataInCache:
    def test_returns_mocked_data_in_development(self):
        with (
            patch(
                "sensors.utils.cache_sensors_data.environment_is_development",
                return_value=True,
            ),
        ):
            assert get_sensors_data_in_cache() == MOCKED_SENSORS_DATA

    def test_returns_cache_content_outside_development(self):
        cache_content = {"38:1F:8D:65:E9:1C": {"name": "TH05-65E91C"}}

        with (
            patch(
                "sensors.utils.cache_sensors_data.environment_is_development",
                return_value=False,
            ),
            patch(
                "sensors.utils.cache_sensors_data.cache.get",
                return_value=cache_content,
            ),
        ):
            assert get_sensors_data_in_cache() == cache_content

    def test_returns_empty_dict_when_cache_is_empty_outside_development(self):
        with (
            patch(
                "sensors.utils.cache_sensors_data.environment_is_development",
                return_value=False,
            ),
            patch("sensors.utils.cache_sensors_data.cache.get", return_value={}),
        ):
            assert get_sensors_data_in_cache() == {}


DATA_IN_CACHE = {
    "38:1F:8D:65:E9:1C": {
        "mac_address": "38:1F:8D:65:E9:1C",
        "name": "TH05-65E91C",
        "rssi": -87,
        "measurements": {
            "battery": 60,
            "temperature": 20.69,
            "humidity": 54.480000000000004,
            "dt": "2025-10-15T12:59:32.465Z",
        },
        "previous_measurements": {
            "battery": 60,
            "temperature": 20.68,
            "humidity": 54.54,
            "dt": "2025-10-15T12:58:37.566Z",
        },
    },
    "38:1F:8D:B2:1F:44": {
        "mac_address": "38:1F:8D:B2:1F:44",
        "name": "TH05-B21F44",
        "rssi": -85,
        "measurements": {
            "battery": 54,
            "temperature": 21.94,
            "humidity": 50.9,
            "dt": "2025-10-15T12:59:22.745Z",
        },
        "previous_measurements": {
            "battery": 54,
            "temperature": 21.95,
            "humidity": 50.88,
            "dt": "2025-10-15T12:58:32.855Z",
        },
    },
}


def test_get_sensor_data_in_cache_real_case():
    with (
        patch(
            "sensors.utils.cache_sensors_data.get_sensors_data_in_cache",
            return_value=DATA_IN_CACHE,
        ),
    ):
        assert get_sensor_data_in_cache("38:1F:8D:65:E9:1C") == {
            "mac_address": "38:1F:8D:65:E9:1C",
            "name": "TH05-65E91C",
            "rssi": -87,
            "measurements": {
                "battery": 60,
                "temperature": 20.69,
                "humidity": 54.480000000000004,
                "dt": "2025-10-15T12:59:32.465Z",
            },
            "previous_measurements": {
                "battery": 60,
                "temperature": 20.68,
                "humidity": 54.54,
                "dt": "2025-10-15T12:58:37.566Z",
            },
        }


@pytest.mark.parametrize(
    "cache_data, mac_address, excepted",
    [
        ({}, "mac", None),
        ({"some": "data"}, "mac", None),
        ({"mac": "data"}, "mac", "data"),
        ({"mac": {"other": "data"}}, "mac", {"other": "data"}),
        ({"mac": {"other": "data"}}, {}, None),
        ({"mac": {"other": "data"}}, [], None),
        ({"mac": {"other": "data"}}, 1, None),
    ],
)
def test_get_sensor_data_in_cache_not_other_cases(cache_data, mac_address, excepted):
    with (
        patch(
            "sensors.utils.cache_sensors_data.get_sensors_data_in_cache",
            return_value=cache_data,
        ),
    ):
        assert get_sensor_data_in_cache(mac_address) == excepted
