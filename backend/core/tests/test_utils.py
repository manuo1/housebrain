import pytest
from core.utils.utils import (
    colored_text,
    watt_to_ampere,
    ampere_to_watt,
    is_new_hour,
    decode_byte,
)
from core.constants import DEFAULT_VOLTAGE, TerminalColor
from datetime import datetime


@pytest.mark.parametrize(
    "text, color, expected",
    [
        ("Hello, World!", TerminalColor.RED, "\033[91mHello, World!\033[0m"),
        ("Success!", TerminalColor.GREEN, "\033[92mSuccess!\033[0m"),
        ("Warning!", TerminalColor.YELLOW, "\033[93mWarning!\033[0m"),
    ],
)
def test_colored_text(text, color, expected):
    assert colored_text(text, color) == expected


@pytest.mark.parametrize(
    "watt, expected",
    [
        (10, 10 / DEFAULT_VOLTAGE),
        (0, 0),
        (-5, -5 / DEFAULT_VOLTAGE),
        (-1.234, -1.234 / DEFAULT_VOLTAGE),
        ("not_a_number", None),
        (None, None),
        ([], None),
    ],
)
def test_watt_to_ampere(watt, expected):
    assert watt_to_ampere(watt) == expected


@pytest.mark.parametrize(
    "intensity, expected",
    [
        (10, 10 * DEFAULT_VOLTAGE),
        (0, 0),
        (-5, -5 * DEFAULT_VOLTAGE),
        (-1.234, -1.234 * DEFAULT_VOLTAGE),
        ("not_a_number", None),
        (None, None),
        ([], None),
    ],
)
def test_ampere_to_watt(intensity, expected):
    assert ampere_to_watt(intensity) == expected


@pytest.mark.parametrize(
    "old_datetime, new_datetime, expected",
    [
        (
            datetime(2025, 5, 11, 14, 30),
            datetime(2025, 5, 11, 15, 5),
            True,
        ),
        (
            datetime(2025, 5, 11, 14, 30),
            datetime(2025, 5, 11, 14, 59),
            False,
        ),
        (
            datetime(2025, 5, 11, 14, 0),
            datetime(2025, 5, 11, 13, 59),
            False,
        ),
        (datetime(2025, 5, 11, 14, 0), "not_a_datetime", False),
        ("not_a_datetime", datetime(2025, 5, 11, 15, 0), False),
    ],
)
def test_is_new_hour(old_datetime, new_datetime, expected):
    assert is_new_hour(old_datetime, new_datetime) == expected


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
