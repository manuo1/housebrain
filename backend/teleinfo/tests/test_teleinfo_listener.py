from datetime import datetime, timezone
from unittest.mock import patch

import pytest
import serial
from freezegun import freeze_time
from teleinfo.constants import REQUIRED_TELEINFO_KEYS
from teleinfo.listener import TeleinfoListener

NOW_DATETIME = datetime(2025, 5, 12, 10, tzinfo=timezone.utc)
START_BUFFER = {"ADCO": "021728123456"}
COMPLETE_BUFFER = {key: "value" for key in REQUIRED_TELEINFO_KEYS}
INCOMPLETE_BUFFER = {key: "value" for key in REQUIRED_TELEINFO_KEYS if key != "ISOUSC"}


@pytest.mark.parametrize(
    "new_serial, excepted_buffer",
    [
        (b"ADCO 021728123456 @\r\n", START_BUFFER),  # First teleinfo key
        (b"OPTARIF HC.. <\r\n", {}),  # Not First teleinfo key
        (None, {}),
    ],
)
@patch("teleinfo.listener.cache")
@patch("teleinfo.listener.notify_watchdog")
def test_process_data_when_buffer_is_empty(
    mock_notify_watchdog, mock_cache, new_serial, excepted_buffer
):
    listener = TeleinfoListener()
    listener._process_data(new_serial)
    assert listener.buffer == excepted_buffer
    assert listener.teleinfo == {}


@pytest.mark.parametrize(
    "new_serial, excepted_buffer",
    [
        (b"ADCO 021728123456 @\r\n", START_BUFFER),  # First teleinfo key
        (b"OPTARIF HC.. <\r\n", {**START_BUFFER, "OPTARIF": "HC.."}),
        (None, START_BUFFER),
    ],
)
@patch("teleinfo.listener.cache")
@patch("teleinfo.listener.notify_watchdog")
def test_process_data_when_buffer_is_not_empty(
    mock_notify_watchdog, mock_cache, new_serial, excepted_buffer
):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()
    listener._process_data(new_serial)
    assert listener.buffer == excepted_buffer
    assert listener.teleinfo == {}


@pytest.mark.parametrize(
    "new_serial, excepted_buffer, excepted_teleinfo",
    [
        # Adding missing key
        # = buffer is complete = create teleinfo
        (
            b"ISOUSC 45 ?\r\n",
            {},
            {
                **INCOMPLETE_BUFFER,
                "ISOUSC": "45",
                "last_read": NOW_DATETIME.isoformat(),
            },
        ),
        # Adding new key (not a REQUIRED_TELEINFO_KEYS)
        # = buffer is updated but not complete = teleinfo stay empty
        (
            b"HCHP 056567645 ?\r\n",
            {**INCOMPLETE_BUFFER, "HCHP": "056567645"},
            {},
        ),
        # Adding incorrect serial
        # = buffer is not updated and teleinfo stay empty
        (
            b"INCORRECT SERIAL\r\n",
            {**INCOMPLETE_BUFFER},
            {},
        ),
    ],
)
@freeze_time(NOW_DATETIME)
@patch("teleinfo.listener.cache")
@patch("teleinfo.listener.notify_watchdog")
def test_process_data_when_buffer_is_only_missing_one_key_to_be_complete(
    mock_notify_watchdog, mock_cache, new_serial, excepted_buffer, excepted_teleinfo
):
    listener = TeleinfoListener()
    listener.buffer = INCOMPLETE_BUFFER.copy()

    listener._process_data(new_serial)

    assert listener.buffer == excepted_buffer
    assert listener.teleinfo == excepted_teleinfo


@pytest.mark.parametrize(
    "in_waiting, readline, excepted_buffer",
    [
        (True, b"ISOUSC 45 ?\r\n", {**START_BUFFER, "ISOUSC": "45"}),
        (False, "", START_BUFFER),
    ],
)
@patch("serial.Serial")
@patch("teleinfo.listener.cache")
@patch("teleinfo.listener.notify_watchdog")
@patch("time.sleep", return_value=None)
def test_fetch_data(
    mock_notify_watchdog,
    mock_cache,
    mock_sleep,
    mock_serial,
    in_waiting,
    readline,
    excepted_buffer,
):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()

    mock_connection = mock_serial.return_value
    mock_connection.in_waiting = in_waiting
    mock_connection.readline.return_value = readline

    listener._fetch_data(mock_connection)

    assert listener.buffer == excepted_buffer


@patch("serial.Serial")
@patch("time.sleep", return_value=None)
@patch("teleinfo.listener.cache")
@patch("teleinfo.listener.notify_watchdog")
def test_fetch_data_raise_serial_exception(
    mock_notify_watchdog, mock_cache, mock_sleep, mock_serial
):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()
    mock_connection = mock_serial.return_value
    mock_connection.in_waiting = True
    mock_connection.readline.side_effect = serial.SerialException()
    # assert nothing breaks in case of an exception and that the buffer doesn't change.
    assert listener.buffer == START_BUFFER


@patch("serial.Serial.open", side_effect=serial.SerialException())
@patch("time.sleep", return_value=None)
@patch("teleinfo.listener.cache")
@patch("teleinfo.listener.notify_watchdog")
def test_listen_if_serial_exception(
    mock_notify_watchdog, mock_cache, mock_sleep, mock_serial
):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()
    listener.start()
    # assert nothing breaks in case of an exception and that the buffer doesn't change.
    assert listener.buffer == START_BUFFER
