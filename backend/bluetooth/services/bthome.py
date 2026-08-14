def decode_bthome_payload(payload: bytes) -> dict | None:
    """
    Decode the Bluetooth BTHome payload.

    Args:
        payload (bytes): Raw data sent by the sensor.

    Returns:
        dict | None: A dictionary containing the measurements if decoding is successful, otherwise None.
    """
    if len(payload) < 5:
        return None

    # Measurement types according to the BTHome format (https://bthome.io/format/)
    # byte_size = number of payload bytes this measurement's value occupies
    measurement_types = {
        0x01: ("battery", "uint8", 1, 1),
        0x02: ("temperature", "sint16", 0.01, 2),
        0x03: ("humidity", "uint16", 0.01, 2),
    }

    measurements = {}
    payload = payload[3:]  # Remove unnecessary flags at the beginning of the payload
    i = 0

    while i < len(payload):
        obj_id = payload[i]
        i += 1

        try:
            name, data_type, factor, byte_size = measurement_types[obj_id]
        except KeyError:
            break

        if i + byte_size > len(payload):
            # Truncated/malformed payload: not enough bytes left for this
            # measurement's value. Stop here instead of reading past the end
            # (uint8) or silently computing a bogus value from partial bytes
            # (sint16/uint16).
            break

        if data_type == "sint16":
            value = int.from_bytes(payload[i : i + 2], byteorder="little", signed=True)
        elif data_type == "uint16":
            value = int.from_bytes(payload[i : i + 2], byteorder="little", signed=False)
        elif data_type == "uint8":
            value = payload[i]

        i += byte_size
        measurements[name] = value * factor

    return measurements if measurements else None
