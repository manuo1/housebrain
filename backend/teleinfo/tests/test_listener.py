import pytest
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
    listener.buffer = START_BUFFER
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
