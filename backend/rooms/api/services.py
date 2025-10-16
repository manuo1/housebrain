from core.utils.date_utils import is_delta_within_one_minute, parse_iso_datetime
from django.utils import timezone
from rooms.api.utils import (
    calculate_radiator_state,
    calculate_temperature_trend,
    get_mac_short,
)
from sensors.services.rssi import rssi_to_signal_strength


def add_temperature_measurements_to_rooms(
    rooms_data: list[dict], sensors_cache: dict
) -> None:
    """
    Enrich room dicts with real-time temperature sensor measurements from cache.
    """
    default_temperature_sensor_data = {
        "temperature_sensor__rssi": None,
        "temperature_sensor__current_temperature": None,
        "temperature_sensor__current_dt": None,
        "temperature_sensor__previous_temperature": None,
        "temperature_sensor__previous_dt": None,
    }
    for room in rooms_data:
        room.update(default_temperature_sensor_data)

        mac_address = room.get("temperature_sensor__mac_address")

        if not mac_address:
            continue

        sensor = sensors_cache.get(mac_address)

        if not sensor:
            continue

        measurements = sensor.get("measurements", {})
        previous_measurements = sensor.get("previous_measurements", {})

        room.update(
            {
                "temperature_sensor__rssi": sensor.get("rssi"),
                "temperature_sensor__current_temperature": measurements.get(
                    "temperature"
                ),
                "temperature_sensor__current_dt": measurements.get("dt"),
                "temperature_sensor__previous_temperature": previous_measurements.get(
                    "temperature"
                ),
                "temperature_sensor__previous_dt": previous_measurements.get("dt"),
            }
        )


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

    if mode == "thermostat":
        value = room_dict.get("current_setpoint")
    elif mode == "manual":
        value = room_dict.get("current_on_off_state")

    return {"mode": mode, "value": value}


def _transform_temperature(room_dict: dict) -> dict:
    """Transform temperature sensor data for API response."""

    temperature_data = {
        "id": room_dict.get("temperature_sensor__id"),
        "mac_short": get_mac_short(room_dict.get("temperature_sensor__mac_address")),
        "signal_strength": rssi_to_signal_strength(
            room_dict.get("temperature_sensor__rssi")
        ),
        "measurements": {
            "temperature": None,
            "trend": None,
        },
    }

    # Add current temperature if it is recent
    current_temperature = room_dict.get("temperature_sensor__current_temperature")

    if current_temperature is None:
        return temperature_data

    current_temperature_dt = parse_iso_datetime(
        room_dict.get("temperature_sensor__current_dt")
    )

    if current_temperature_dt is None or not is_delta_within_one_minute(
        current_temperature_dt, timezone.now()
    ):
        return temperature_data

    temperature_data["measurements"]["temperature"] = current_temperature

    # Add temperature trend if the two measurements are close enough
    previous_temperature = room_dict.get("temperature_sensor__previous_temperature")
    previous_temperature_dt = parse_iso_datetime(
        room_dict.get("temperature_sensor__previous_dt")
    )
    if (
        not previous_temperature_dt
        or not previous_temperature
        or not is_delta_within_one_minute(
            current_temperature_dt, previous_temperature_dt
        )
    ):
        return temperature_data

    temperature_data["measurements"]["trend"] = calculate_temperature_trend(
        current_temperature, previous_temperature
    )

    return temperature_data


def _transform_radiator(room_dict: dict) -> dict:
    """Transform radiator data for API response."""
    return {
        "id": room_dict.get("radiator__id"),
        "state": calculate_radiator_state(
            room_dict.get("radiator__requested_state"),
            room_dict.get("radiator__actual_state"),
        ),
    }
