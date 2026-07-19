def decode_byte(byte_data: bytes) -> str | None:
    """Decode a bytes object as UTF-8, returning None if decoding fails or input isn't bytes."""
    try:
        return byte_data.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
