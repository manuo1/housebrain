def decode_byte(byte_data: bytes) -> str | None:
    try:
        return byte_data.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return None
