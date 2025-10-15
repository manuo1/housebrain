from rooms.api.services import add_temperature_measurements_to_rooms

ROOMS_DATA = [
    {
        "id": 1,
        "temperature_sensor__mac_address": "38:1F:8D:65:E9:1C",
    }
]
SENSORS_CACHE = {
    "38:1F:8D:65:E9:1C": {
        "rssi": -87,
        "measurements": {
            "temperature": 20.69,
            "dt": "2025-10-15T12:59:32.465Z",
        },
        "previous_measurements": {
            "temperature": 20.68,
            "dt": "2025-10-15T12:58:37.566Z",
        },
    },
}


def test_add_temperature_measurements_to_rooms_with_no_room():
    rooms_data = []
    sensors_cache = SENSORS_CACHE
    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)
    assert rooms_data == []


def test_add_temperature_measurements_to_rooms_add_default_fields():
    rooms_data = ROOMS_DATA

    sensors_cache = {}

    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)

    assert rooms_data == [
        {
            "id": 1,
            "temperature_sensor__mac_address": "38:1F:8D:65:E9:1C",
            "temperature_sensor__rssi": None,
            "temperature_sensor__current_temperature": None,
            "temperature_sensor__current_dt": None,
            "temperature_sensor__previous_temperature": None,
            "temperature_sensor__previous_dt": None,
        }
    ]


def test_add_temperature_measurements_to_rooms_add_cache_data():
    rooms_data = ROOMS_DATA

    sensors_cache = SENSORS_CACHE
    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)

    assert rooms_data == [
        {
            "id": 1,
            "temperature_sensor__mac_address": "38:1F:8D:65:E9:1C",
            "temperature_sensor__rssi": -87,
            "temperature_sensor__current_temperature": 20.69,
            "temperature_sensor__current_dt": "2025-10-15T12:59:32.465Z",
            "temperature_sensor__previous_temperature": 20.68,
            "temperature_sensor__previous_dt": "2025-10-15T12:58:37.566Z",
        }
    ]


def test_multiple_rooms_and_sensors():
    rooms_data = [
        {"id": 1, "temperature_sensor__mac_address": "38:1F:8D:65:E9:1C"},
        {"id": 2, "temperature_sensor__mac_address": "UNKNOWN"},
        {"id": 3},  # pas de capteur
    ]
    sensors_cache = SENSORS_CACHE
    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)
    assert rooms_data[0]["temperature_sensor__rssi"] == -87
    assert rooms_data[1]["temperature_sensor__rssi"] is None
    assert rooms_data[2]["temperature_sensor__rssi"] is None


def test_sensor_with_partial_data():
    rooms_data = [{"id": 1, "temperature_sensor__mac_address": "38:1F:8D:65:E9:1C"}]
    sensors_cache = {
        "38:1F:8D:65:E9:1C": {
            "rssi": -70,
            "measurements": {},  # vide
            # previous_measurements manquant
        }
    }
    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)
    room = rooms_data[0]
    assert room["temperature_sensor__rssi"] == -70
    assert room["temperature_sensor__current_temperature"] is None
    assert room["temperature_sensor__previous_temperature"] is None


def test_room_with_unknown_mac():
    rooms_data = [{"id": 1, "temperature_sensor__mac_address": "UNKNOWN"}]
    sensors_cache = SENSORS_CACHE
    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)
    assert rooms_data[0]["temperature_sensor__rssi"] is None


def test_room_without_sensor_mac_address():
    rooms_data = [{"id": 1}]
    sensors_cache = SENSORS_CACHE
    add_temperature_measurements_to_rooms(rooms_data, sensors_cache)
    assert rooms_data[0]["temperature_sensor__rssi"] is None
