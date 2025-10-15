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
