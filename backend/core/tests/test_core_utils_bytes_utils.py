import pytest
from core.utils.bytes_utils import decode_byte


@pytest.mark.parametrize(
    "byte_data, expected",
    [
        (b"Hello, World!", "Hello, World!"),  # Valid UTF-8 bytes
        (b"\xe2\x82\xac", "€"),  # UTF-8 encoded Euro symbol
        (b"", ""),  # Empty byte string
        (None, None),  # None input
        ("Not bytes", None),  # Invalid type (string instead of bytes)
        (b"\xff\xfe\xfd", None),  # Invalid UTF-8 sequence
        (b"HCHP 056567645 ?\r\n", "HCHP 056567645 ?\r\n"),
    ],
)
def test_decode_byte(byte_data, expected):
    assert decode_byte(byte_data) == expected
