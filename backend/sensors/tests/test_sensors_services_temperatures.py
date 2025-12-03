from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sensors.services.temperatures import get_sensor_temperatures


def test_get_sensor_temperatures_real_case():
    sensor_data_in_cache = {
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

    with (
        patch(
            "sensors.services.temperatures.get_sensor_data_in_cache",
            return_value=sensor_data_in_cache,
        ),
    ):
        assert get_sensor_temperatures("38:1F:8D:65:E9:1C") == {
            "temperature": 20.69,
            "dt": datetime(2025, 10, 15, 12, 59, 32, 465000, tzinfo=timezone.utc),
            "previous_temperature": 20.68,
            "previous_dt": datetime(
                2025, 10, 15, 12, 58, 37, 566000, tzinfo=timezone.utc
            ),
        }


DEFAULT_SENSOR_TEMPERATURES = {
    "temperature": None,
    "dt": None,
    "previous_temperature": None,
    "previous_dt": None,
}


@pytest.mark.parametrize(
    "sensor_data_in_cache, excepted",
    [
        ([], DEFAULT_SENSOR_TEMPERATURES),
        ("a", DEFAULT_SENSOR_TEMPERATURES),
        ({}, DEFAULT_SENSOR_TEMPERATURES),
        (
            {
                "previous_measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T00:00:00Z",
                },
            },
            DEFAULT_SENSOR_TEMPERATURES,
        ),
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T00:00:00Z",
                },
            },
            DEFAULT_SENSOR_TEMPERATURES,
        ),
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T00:00:00Z",
                },
                "previous_measurements": {
                    "temperature": 1,
                },
            },
            DEFAULT_SENSOR_TEMPERATURES,
        ),
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T00:00:00Z",
                },
                "previous_measurements": {
                    "dt": "2025-10-15T00:00:00Z",
                },
            },
            DEFAULT_SENSOR_TEMPERATURES,
        ),
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T00:00:00Z",
                },
                "previous_measurements": {},
            },
            DEFAULT_SENSOR_TEMPERATURES,
        ),
    ],
)
def test_get_sensor_temperatures_other_case(sensor_data_in_cache, excepted):
    with (
        patch(
            "sensors.services.temperatures.get_sensor_data_in_cache",
            return_value=sensor_data_in_cache,
        ),
    ):
        print(get_sensor_temperatures("mac"))
        assert get_sensor_temperatures("mac") == excepted
