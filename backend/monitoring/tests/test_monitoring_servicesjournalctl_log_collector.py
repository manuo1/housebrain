import json
import subprocess
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from core.constants import MICROSECONDS_PER_SECOND
from freezegun import freeze_time
from monitoring.services.journalctl_log_collector import (
    PRIORITY_MAP,
    SERVICES,
    collect_journalctl_logs,
    get_log_level,
    get_logged_at,
    get_message,
    get_service_logs,
    parse_json_line,
)


def test_get_service_logs_normal():
    fake_output = '{"MESSAGE": "Service started"}\n'

    with patch(
        "monitoring.services.journalctl_log_collector.subprocess.check_output"
    ) as mock_check_output:
        mock_check_output.return_value = fake_output

        result = get_service_logs("some_service")

        assert result == fake_output


def test_get_service_logs_timeout():
    with patch(
        "monitoring.services.journalctl_log_collector.subprocess.check_output"
    ) as mock_check_output:
        mock_check_output.side_effect = subprocess.TimeoutExpired(
            cmd="journalctl", timeout=30
        )
        result = get_service_logs("some_service")
        assert result == ""


def test_get_service_logs_calledprocesserror():
    with patch(
        "monitoring.services.journalctl_log_collector.subprocess.check_output"
    ) as mock_check_output:
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="journalctl", output="error message"
        )
        result = get_service_logs("redis-server.service")
        assert result == ""


@pytest.mark.parametrize(
    "line, expected",
    [
        ('{"a": "b"}', {"a": "b"}),
        ("{}", {}),
        ({"a": "b"}, {}),
        ([], {}),
        (None, {}),
        ("a", {}),
    ],
)
def test_parse_json_line(line, expected):
    result = parse_json_line("some_service", line)
    assert result == expected


@pytest.mark.parametrize(
    "line_data, expected",
    [
        ({"PRIORITY": "1"}, "ALERT"),
        ('{"PRIORITY": "1"}', "UNKNOWN"),
        ([], "UNKNOWN"),
        (None, "UNKNOWN"),
        ("a", "UNKNOWN"),
    ],
)
def test_get_log_level(line_data, expected):
    result = get_log_level("some_service", line_data)
    assert result == expected


@pytest.mark.parametrize(
    "line_data, expected",
    [
        ({"MESSAGE": "a"}, "a"),
        ('{"MESSAGE": "a"}', ""),
        ([], ""),
        (None, ""),
        ("a", ""),
    ],
)
def test_get_message(line_data, expected):
    result = get_message("some_service", line_data)
    assert result == expected


DT_NOW = datetime(2025, 10, 24, 12, tzinfo=timezone.utc)
DT1 = datetime(2025, 10, 24, 8, tzinfo=timezone.utc)
DT1_MICRO_TIMESTAMP = DT1.timestamp() * MICROSECONDS_PER_SECOND
DT2 = datetime(2025, 10, 24, 9, tzinfo=timezone.utc)
DT2_MICRO_TIMESTAMP = DT2.timestamp() * MICROSECONDS_PER_SECOND


@freeze_time(DT_NOW)
@pytest.mark.parametrize(
    "line_data, expected",
    [
        ({"__REALTIME_TIMESTAMP": DT1_MICRO_TIMESTAMP}, DT1),
        ({"A_KEY": DT1_MICRO_TIMESTAMP}, DT_NOW),
        ('{"__REALTIME_TIMESTAMP": DT_MICRO_TIMESTAMP}', DT_NOW),
        ([], DT_NOW),
        (None, DT_NOW),
        ("a", DT_NOW),
    ],
)
def test_get_logged_at(line_data, expected):
    result = get_logged_at("some_service", line_data)
    assert result == expected


@freeze_time(DT_NOW)
def test_collect_journalctl_logs():
    LOGS_DICT_1 = {
        "__REALTIME_TIMESTAMP": DT1_MICRO_TIMESTAMP,
        "PRIORITY": "1",
        "MESSAGE": "a message",
    }
    LOGS_DICT_2 = {
        "__REALTIME_TIMESTAMP": DT2_MICRO_TIMESTAMP,
        "PRIORITY": "3",
        "MESSAGE": "another message",
    }

    fake_output = (
        "\n".join(json.dumps(log) for log in [LOGS_DICT_1, LOGS_DICT_2]) + "\n"
    )

    with patch(
        "monitoring.services.journalctl_log_collector.get_service_logs"
    ) as mock_get_service_logs:
        mock_get_service_logs.return_value = fake_output

        result = collect_journalctl_logs()
        expected = []
        for service in SERVICES:
            for log_dict, dt in zip([LOGS_DICT_1, LOGS_DICT_2], [DT1, DT2]):
                expected.append(
                    {
                        "service": service,
                        "level": PRIORITY_MAP[log_dict["PRIORITY"]],
                        "message": log_dict["MESSAGE"],
                        "logged_at": dt,
                    }
                )

        assert result == expected
