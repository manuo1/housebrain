import pytest
from actuators.models import Radiator
from freezegun import freeze_time
from rooms.api.constants import ApiRadiatorState, TemperatureTrend
from rooms.api.services import (
    _transform_heating,
    _transform_radiator,
    _transform_temperature,
    add_temperature_measurements_to_rooms,
)
from rooms.models import Room

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


@pytest.mark.parametrize(
    "requested, actual, expected_state",
    [
        # --- cas standards ---
        (Radiator.RequestedState.ON, Radiator.ActualState.ON, ApiRadiatorState.ON),
        (
            Radiator.RequestedState.ON,
            Radiator.ActualState.OFF,
            ApiRadiatorState.TURNING_ON,
        ),
        (Radiator.RequestedState.OFF, Radiator.ActualState.OFF, ApiRadiatorState.OFF),
        (
            Radiator.RequestedState.OFF,
            Radiator.ActualState.ON,
            ApiRadiatorState.SHUTTING_DOWN,
        ),
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.OFF,
            ApiRadiatorState.LOAD_SHED,
        ),
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.ON,
            ApiRadiatorState.SHUTTING_DOWN,
        ),
        # --- cas indéfinis ---
        (
            Radiator.RequestedState.ON,
            Radiator.ActualState.UNDEFINED,
            ApiRadiatorState.UNDEFINED,
        ),
        (None, Radiator.ActualState.OFF, None),
        (Radiator.RequestedState.ON, None, None),
        (None, None, None),
    ],
)
def test_transform_radiator_various_states(requested, actual, expected_state):
    room_dict = {
        "radiator__id": 1,
        "radiator__requested_state": requested,
        "radiator__actual_state": actual,
    }

    result = _transform_radiator(room_dict)

    assert result["id"] == 1
    assert result["state"] == expected_state


def test_transform_radiator_missing_id():
    """Si l'id du radiateur est absent, on doit quand même retourner state."""
    room_dict = {
        "radiator__requested_state": Radiator.RequestedState.ON,
        "radiator__actual_state": Radiator.ActualState.OFF,
    }

    result = _transform_radiator(room_dict)

    assert result["id"] is None
    assert result["state"] == ApiRadiatorState.TURNING_ON


def test_transform_radiator_extra_fields_are_ignored():
    """Les champs inutiles dans le dict ne doivent pas interférer."""
    room_dict = {
        "radiator__id": 3,
        "radiator__requested_state": Radiator.RequestedState.OFF,
        "radiator__actual_state": Radiator.ActualState.ON,
        "temperature_sensor__id": 99,  # bruit
    }

    result = _transform_radiator(room_dict)

    assert result == {
        "id": 3,
        "state": ApiRadiatorState.SHUTTING_DOWN,
    }


@pytest.mark.parametrize(
    "room_dict, expected_mode, expected_value",
    [
        # --- mode thermostat ---
        (
            {
                "heating_control_mode": Room.HeatingControlMode.THERMOSTAT,
                "current_setpoint": 21.5,
            },
            Room.HeatingControlMode.THERMOSTAT,
            21.5,
        ),
        (
            {
                "heating_control_mode": Room.HeatingControlMode.THERMOSTAT,
                "current_setpoint": None,
            },
            Room.HeatingControlMode.THERMOSTAT,
            None,
        ),
        # --- mode manuel ---
        (
            {
                "heating_control_mode": Room.HeatingControlMode.ONOFF,
                "current_on_off_state": Room.CurrentHeatingState.ON,
            },
            Room.HeatingControlMode.ONOFF,
            Room.CurrentHeatingState.ON,
        ),
        (
            {
                "heating_control_mode": Room.HeatingControlMode.ONOFF,
                "current_on_off_state": None,
            },
            Room.HeatingControlMode.ONOFF,
            None,
        ),
        # --- mode inconnu ---
        (
            {
                "heating_control_mode": Room.HeatingControlMode.ONOFF,
                "current_on_off_state": None,
            },
            Room.HeatingControlMode.ONOFF,
            None,
        ),
        (
            {"heating_control_mode": None, "current_setpoint": 20.0},
            None,
            None,
        ),
        # --- dictionnaire vide ---
        ({}, None, None),
    ],
)
def test_transform_heating_various_modes(room_dict, expected_mode, expected_value):
    """Vérifie la logique de sélection mode/value selon le mode de chauffage."""
    result = _transform_heating(room_dict)

    assert result == {
        "mode": expected_mode,
        "value": expected_value,
    }


def test_transform_heating_ignores_extra_fields():
    """Les champs inutiles ne doivent pas interférer."""
    room_dict = {
        "heating_control_mode": "on_off",
        "current_on_off_state": "off",
        "random_field": 123,
        "temperature_sensor__id": 99,
    }

    result = _transform_heating(room_dict)

    assert result == {"mode": "on_off", "value": "off"}


BASE_ROOM_DATA = {
    "temperature_sensor__id": 10,
    "temperature_sensor__mac_address": "AA:BB:CC:DD:EE:FF",
    "temperature_sensor__rssi": -75,
}


@pytest.mark.parametrize(
    "now_iso, current_dt, delta_ok, expected_temp, expected_trend",
    [
        # --- Cas 1 : mesure récente (<1 min) + trend positive ---
        (
            "2025-10-16T10:00:00Z",
            "2025-10-16T09:59:30Z",  # 30s avant
            True,
            21.0,
            TemperatureTrend.UP,
        ),
        # --- Cas 2 : mesure récente mais trend quasi stable (diff < 0.1) ---
        (
            "2025-10-16T10:00:00Z",
            "2025-10-16T09:59:30Z",
            True,
            20.05,
            TemperatureTrend.SAME,
        ),
        # --- Cas 3 : mesure récente mais trend descendante ---
        (
            "2025-10-16T10:00:00Z",
            "2025-10-16T09:59:30Z",
            True,
            19.5,
            TemperatureTrend.DOWN,
        ),
        # --- Cas 4 : mesure trop ancienne (>2 min) → pas de temperature ---
        (
            "2025-10-16T10:00:00Z",
            "2025-10-16T09:57:30Z",  # 2m30 avant
            False,
            None,
            None,
        ),
    ],
)
@freeze_time("2025-10-16T10:00:00Z")
def test_transform_temperature_with_various_deltas(
    now_iso, current_dt, delta_ok, expected_temp, expected_trend
):
    """Teste la logique complète de température : fraicheur et tendance."""
    room_dict = {
        **BASE_ROOM_DATA,
        "temperature_sensor__current_temperature": expected_temp
        if expected_temp
        else 20.0,
        "temperature_sensor__current_dt": current_dt,
        "temperature_sensor__previous_temperature": 20.0,
        "temperature_sensor__previous_dt": "2025-10-16T09:59:00Z",
    }

    result = _transform_temperature(room_dict)

    assert result["id"] == 10
    assert result["mac_short"].endswith("EE:FF")  # get_mac_short = 3 derniers segments
    assert isinstance(result["signal_strength"], int)

    if not delta_ok:
        # Trop ancien → aucun relevé
        assert result["measurements"]["temperature"] is None
        assert result["measurements"]["trend"] is None
    else:
        # Relevé récent
        assert result["measurements"]["temperature"] == pytest.approx(
            expected_temp, 0.01
        )
        assert result["measurements"]["trend"] == expected_trend


@freeze_time("2025-10-16T10:00:00Z")
def test_transform_temperature_missing_current_temperature():
    """Aucune temperature actuelle → pas de mesures."""
    room_dict = {
        **BASE_ROOM_DATA,
        "temperature_sensor__current_temperature": None,
    }

    result = _transform_temperature(room_dict)

    assert result["measurements"] == {"temperature": None, "trend": None}


@freeze_time("2025-10-16T10:00:00Z")
def test_transform_temperature_missing_previous_values():
    """Pas de valeur précédente → trend non calculée."""
    room_dict = {
        **BASE_ROOM_DATA,
        "temperature_sensor__current_temperature": 21.0,
        "temperature_sensor__current_dt": "2025-10-16T09:59:40Z",
        "temperature_sensor__previous_temperature": None,
        "temperature_sensor__previous_dt": None,
    }

    result = _transform_temperature(room_dict)

    assert result["measurements"]["temperature"] == 21.0
    assert result["measurements"]["trend"] is None


@freeze_time("2025-10-16T10:00:00Z")
def test_transform_temperature_invalid_datetime():
    """Datetime invalide doit être ignorée."""
    room_dict = {
        **BASE_ROOM_DATA,
        "temperature_sensor__current_temperature": 21.0,
        "temperature_sensor__current_dt": "BAD_FORMAT",
    }

    result = _transform_temperature(room_dict)

    assert result["measurements"]["temperature"] is None
    assert result["measurements"]["trend"] is None


def test_transform_temperature_rssi_signal_strength_levels():
    """Vérifie la conversion du RSSI en barres de signal."""
    rssi_values = [-45, -55, -65, -75, -85]
    room_ids = []

    for idx, rssi in enumerate(rssi_values, start=1):
        room_dict = {
            **BASE_ROOM_DATA,
            "temperature_sensor__id": idx,
            "temperature_sensor__rssi": rssi,
        }
        result = _transform_temperature(room_dict)
        room_ids.append(result["id"])
        assert 1 <= result["signal_strength"] <= 5

    assert len(room_ids) == len(rssi_values)
