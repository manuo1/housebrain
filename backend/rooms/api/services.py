from core.utils.temperatures import calculate_temperature_trend
from rooms.api.utils import calculate_radiator_state, get_mac_short
from rooms.models import Room
from bluetooth.services.rssi import rssi_to_signal_strength
from sensors.services.temperatures import get_sensor_temperatures


def add_temperature_measurements_to_rooms(
    rooms_data: list[dict], sensors_cache: dict
) -> None:
    """
    Enrich room dicts with the RSSI of their temperature sensor, read from
    the bluetooth cache. Temperature values themselves are not pulled here:
    _transform_temperature fetches them per-room via get_sensor_temperatures,
    which is also the single source of truth for freshness (used by the
    thermostat too).
    """
    for room in rooms_data:
        room["temperature_sensor__rssi"] = None

        mac_address = room.get("temperature_sensor__mac_address")

        if not mac_address:
            continue

        sensor = sensors_cache.get(mac_address)

        if not sensor:
            continue

        room["temperature_sensor__rssi"] = sensor.get("rssi")


def transform_room_data_for_api(room_dict: dict) -> dict:
    """
    Transform an enriched room dict into the final API format.
    """
    return {
        "id": room_dict.get("id"),
        "name": room_dict.get("name"),
        "heating": _transform_heating(room_dict),
        "temperature": _transform_temperature(room_dict),
        "radiator": _transform_radiator(room_dict),
    }


def _transform_heating(room_dict: dict) -> dict:
    """Transform heating data for API response."""
    mode = room_dict.get("heating_control_mode")
    value = None

    if mode == Room.HeatingControlMode.THERMOSTAT:
        value = room_dict.get("temperature_setpoint")
    elif mode == Room.HeatingControlMode.ONOFF:
        value = room_dict.get("requested_heating_state")

    return {"mode": mode, "value": value}


def _transform_temperature(room_dict: dict) -> dict:
    """
    Transform temperature sensor data for API response. Freshness (current
    < 1min, previous < 2min) is entirely delegated to get_sensor_temperatures,
    the same logic used by the thermostat.
    """
    mac_address = room_dict.get("temperature_sensor__mac_address")

    current_temperature, previous_temperature = (
        get_sensor_temperatures(mac_address) if mac_address else (None, None)
    )

    trend = None
    if current_temperature is not None and previous_temperature is not None:
        trend = calculate_temperature_trend(current_temperature, previous_temperature)

    return {
        "id": room_dict.get("temperature_sensor__id"),
        "mac_short": get_mac_short(mac_address),
        "signal_strength": rssi_to_signal_strength(
            room_dict.get("temperature_sensor__rssi")
        ),
        "measurements": {
            "temperature": current_temperature,
            "trend": trend,
        },
    }


def _transform_radiator(room_dict: dict) -> dict:
    """Transform radiator data for API response."""
    return {
        "id": room_dict.get("radiator__id"),
        "state": calculate_radiator_state(
            room_dict.get("radiator__requested_state"),
            room_dict.get("radiator__actual_state"),
        ),
    }
