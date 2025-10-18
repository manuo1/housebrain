from unittest.mock import patch

import pytest
from actuators.constants import POWER_SAFETY_MARGIN
from teleinfo.constants import FIRST_TELEINFO_FRAME_KEY, REQUIRED_TELEINFO_KEYS
from teleinfo.services import (
    buffer_can_accept_new_data,
    buffer_is_complete,
    calculate_checksum,
    clean_data,
    data_is_valid,
    ensure_power_not_exceeded,
    get_data_in_line,
    split_data,
)


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ("\r\x02Hello World!\x03\n", "Hello World!"),
        ("\r\n\x03\x02", ""),
        ("Hello World!", "Hello World!"),
        ("", ""),
        (None, None),
        (12345, None),
        ({}, None),
        ("HCHP 056567645 ?\r\n", "HCHP 056567645 ?"),
    ],
)
def test_clean_data(input_data, expected_output):
    assert clean_data(input_data) == expected_output


@pytest.mark.parametrize(
    "cleaned_data, expected",
    [
        # OK Valid cases
        ("ADCO 021728123456 =", ["ADCO", "021728123456", "="]),
        ("OPTARIF HC.. <", ["OPTARIF", "HC..", "<"]),
        ("ISOUSC 45 ?", ["ISOUSC", "45", "?"]),
        # NOT OK Edge cases
        ("", [None, None, None]),  # Empty string
        ("ADCO", [None, None, None]),  # Only key
        ("ADCO 021728123456", [None, None, None]),  # Key + value but no checksum
        ("ADCO 021728123456 =", ["ADCO", "021728123456", "="]),  # Normal case
        # OK Handles spaces correctly
        ("ADCO 021728123456  ", ["ADCO", "021728123456", " "]),  # Last char is space
        # NOT OK Invalid types
        (12345, [None, None, None]),  # Not a string
        (None, [None, None, None]),  # NoneType
        # OK Handles weird characters
        ("DATA TEST ~", ["DATA", "TEST", "~"]),
        # more than 3 data
        ("ADCO 021728123456 = EXTRA", [None, None, None]),
        #
        ("HCHP 056567645 ?", ["HCHP", "056567645", "?"]),
    ],
)
def test_split_data(cleaned_data, expected):
    assert split_data(cleaned_data) == expected


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("ADCO", "021728123456", "@"),  # Standard case with valid checksum
        ("OPTARIF", "HC..", "<"),  # Check with another pair
        ("ISOUSC", "45", "?"),  # Example with numbers only
        ("HCHC", "050977332", "*"),  # Another example with large numbers
        ("PTEC", "HP..", " "),  # Example with special characters
        ("PTEC", "", None),  # Empty case
        ("", "HP..", None),  # Empty case
        ("", "", None),  # Empty case
        (None, "VALUE", None),  # Test with 'None' as key
        ("KEY", None, None),  # Test with 'None' as value
        (None, None, None),  # Test with 'None' as key and value
        (123, "VALUE", None),  # Test with a non-string type
        ("HCHP", "056567645", "?"),
    ],
)
def test_calculate_checksum(key, value, expected):
    assert calculate_checksum(key, value) == expected


@pytest.mark.parametrize(
    "key, value, checksum, expected",
    [
        ("ADCO", "021728123456", "@", True),  # Checksum matches
        ("ISOUSC", "45", "X", False),  # Checksum does not match
        (None, "VALUE", "9", False),
        ("KEY", None, "9", False),
        ("KEY", "VALUE", None, False),
        (123, "VALUE", "9", False),
        ("KEY", 456, "9", False),
        ("KEY", "VALUE", 789, False),
        ("", "021728123456", "@", False),
        ("ADCO", "", "@", False),
        ("ADCO", "021728123456", "", False),
        ("HCHP", "056567645", "?", True),
    ],
)
def test_data_is_valid(key, value, checksum, expected):
    assert data_is_valid(key, value, checksum) == expected


@pytest.mark.parametrize(
    "byte_data, expected_key, expected_value",
    [
        (b"ADCO 021728123456 @\r\n", "ADCO", "021728123456"),  # Ok case
        (b"ISOUSC 45 X\r\n", None, None),  # Incorrect Checksum
        (b"BAD DATA\r\n", None, None),
        (b"", None, None),
        (None, None, None),
        (b"TRUNCATED DATA", None, None),
        (b"INVALID CHAR\xff", None, None),
        (b"HCHP 056567645 ?\r\n", "HCHP", "056567645"),
    ],
)
def test_get_data_in_line(byte_data, expected_key, expected_value):
    assert get_data_in_line(byte_data) == (expected_key, expected_value)


@pytest.mark.parametrize(
    "key, buffer, expected",
    [
        # Buffer is empty, first key is valid
        (FIRST_TELEINFO_FRAME_KEY, {}, True),
        # Buffer is empty but key is not the first one
        ("A_KEY", {}, False),
        # Buffer contains the first key
        (FIRST_TELEINFO_FRAME_KEY, {FIRST_TELEINFO_FRAME_KEY: "a"}, True),
        # Buffer has the first key, other keys are allowed
        ("A_KEY", {FIRST_TELEINFO_FRAME_KEY: "a"}, True),
        # Buffer does not contain the first key
        ("A_KEY", {"A_KEY": "a"}, False),
        # Key is not a string
        (123, {FIRST_TELEINFO_FRAME_KEY: "a"}, False),
        # Buffer is not a dictionary
        ("KEY", "not_a_dict", False),
        ("HCHP", {FIRST_TELEINFO_FRAME_KEY: "a"}, True),
    ],
)
def test_buffer_can_accept_new_data(key, buffer, expected):
    assert buffer_can_accept_new_data(key, buffer) == expected


@pytest.mark.parametrize(
    "buffer, expected",
    [
        # All required keys are present
        ({key: "value" for key in REQUIRED_TELEINFO_KEYS}, True),
        # Missing one key
        ({"ADCO": "value", "MOTDETAT": "value", "IINST": "value"}, False),
        # Buffer is empty
        ({}, False),
        # Buffer is not a dictionary
        ("not_a_dict", False),
        # Extra keys are present but all required keys are still there
        (
            {**{key: "value" for key in REQUIRED_TELEINFO_KEYS}, "EXTRA_KEY": "value"},
            True,
        ),
    ],
)
def test_buffer_is_complete(buffer, expected):
    """Test if the buffer is complete with all required teleinfo keys."""
    assert buffer_is_complete(buffer) == expected


def test_load_shedding_triggered():
    """Doit appeler manage_load_shedding si la puissance est trop basse"""
    with (
        patch("teleinfo.services.get_instant_available_power", return_value=0.5),
        patch("teleinfo.services.manage_load_shedding") as mock_shed,
    ):
        ensure_power_not_exceeded()
        mock_shed.assert_called_once_with(0.5)


def test_load_shedding_not_triggered():
    """Ne doit pas appeler manage_load_shedding si la puissance est suffisante"""
    with (
        patch(
            "teleinfo.services.get_instant_available_power",
            return_value=POWER_SAFETY_MARGIN + 1,
        ),
        patch("teleinfo.services.manage_load_shedding") as mock_shed,
    ):
        ensure_power_not_exceeded()
        mock_shed.assert_not_called()


def test_load_shedding_none_power():
    """Doit appeler manage_load_shedding si get_instant_available_power retourne None"""
    with (
        patch("teleinfo.services.get_instant_available_power", return_value=None),
        patch("teleinfo.services.manage_load_shedding") as mock_shed,
    ):
        ensure_power_not_exceeded()
        mock_shed.assert_called_once_with(None)
