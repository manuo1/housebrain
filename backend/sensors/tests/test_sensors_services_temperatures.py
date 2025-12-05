from unittest.mock import patch

import pytest
from freezegun import freeze_time
from sensors.services.temperatures import get_sensor_temperatures


@freeze_time("2025-10-15T13:00:00Z")
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
        assert get_sensor_temperatures("38:1F:8D:65:E9:1C") == (20.69, 20.68)


@pytest.mark.parametrize(
    "sensor_data_in_cache, excepted",
    [
        ([], (None, None)),
        ("a", (None, None)),
        ({}, (None, None)),
        # measurements missing
        (
            {
                "previous_measurements": {
                    "temperature": 2,
                    "dt": "2025-10-15T12:58:30Z",
                },
            },
            (None, 2),
        ),
        # previous_measurements missing
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T12:59:30Z",
                },
            },
            (1, None),
        ),
        # missing dt field
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T12:59:30Z",
                },
                "previous_measurements": {
                    "temperature": 1,
                },
            },
            (1, None),
        ),
        # missing temperature field
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T12:59:30Z",
                },
                "previous_measurements": {
                    "dt": "2025-10-15T12:58:30Z",
                },
            },
            (1, None),
        ),
        # Outdated dt
        (
            {
                "measurements": {
                    "temperature": 1,
                    "dt": "2025-10-15T12:59:30Z",
                },
                "previous_measurements": {
                    "previous_measurements": {
                        "temperature": 2,
                        "dt": "2025-10-15T12:57:30Z",  # <-
                    },
                },
            },
            (1, None),
        ),
    ],
)
@freeze_time("2025-10-15T13:00:00Z")
def test_get_sensor_temperatures_other_case(sensor_data_in_cache, excepted):
    with (
        patch(
            "sensors.services.temperatures.get_sensor_data_in_cache",
            return_value=sensor_data_in_cache,
        ),
    ):
        assert get_sensor_temperatures("mac") == excepted
