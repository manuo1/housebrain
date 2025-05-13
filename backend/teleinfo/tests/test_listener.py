from unittest.mock import patch
import pytest
import serial
from core.constants import LoggerLabel
from teleinfo.constants import REQUIRED_TELEINFO_KEYS
from teleinfo.listener import TeleinfoListener
from freezegun import freeze_time
from datetime import datetime
from zoneinfo import ZoneInfo
from core.settings.base import TIME_ZONE

NOW_DATETIME = datetime(2025, 5, 12, 10, tzinfo=ZoneInfo(TIME_ZONE))
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
def test_process_data_when_buffer_is_empty(new_serial, excepted_buffer):
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
def test_process_data_when_buffer_is_not_empty(new_serial, excepted_buffer):
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
                "created": NOW_DATETIME,
                "last_saved_at": None,
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
def test_process_data_when__buffer_is_only_missing_one_key_to_be_complete(
    new_serial, excepted_buffer, excepted_teleinfo
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
@patch("time.sleep", return_value=None)
def test_fetch_data(mock_sleep, mock_serial, in_waiting, readline, excepted_buffer):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()

    mock_connection = mock_serial.return_value
    mock_connection.in_waiting = in_waiting
    mock_connection.readline.return_value = readline

    listener._fetch_data(mock_connection)

    assert listener.buffer == excepted_buffer


@patch("serial.Serial")
@patch("time.sleep", return_value=None)
def test_fetch_data_raise_serial_exception(mock_sleep, mock_serial):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()
    mock_connection = mock_serial.return_value
    mock_connection.in_waiting = True
    mock_connection.readline.side_effect = serial.SerialException()
    # assert nothing breaks in case of an exception and that the buffer doesn't change.
    assert listener.buffer == START_BUFFER


@patch("serial.Serial.open", side_effect=serial.SerialException())
@patch("time.sleep", return_value=None)
def test_listen_if_serial_exception(mock_sleep, mock_serial):
    listener = TeleinfoListener()
    listener.buffer = START_BUFFER.copy()
    listener._listen()
    # assert nothing breaks in case of an exception and that the buffer doesn't change.
    assert listener.buffer == START_BUFFER


@patch("teleinfo.listener.logger")
def test_start_thread(mock_logger):
    listener = TeleinfoListener()
    assert not listener._thread.is_alive()
    listener.start_thread()
    assert listener._thread.is_alive()
    mock_logger.info.assert_called_once_with(
        f"{LoggerLabel.TELEINFOLISTENER} Thread started."
    )


@patch("teleinfo.listener.logger")
def test_start_thread_when_already_running(mock_logger):
    listener = TeleinfoListener()

    listener.start_thread()
    listener.start_thread()

    mock_logger.warning.assert_called_once_with(
        f"{LoggerLabel.TELEINFOLISTENER} Thread is already running."
    )
