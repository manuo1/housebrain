import logging
import subprocess

import pytest
from core.services import system_metrics
from core.services.system_metrics import (
    USB_DMESG_WINDOW,
    _decode_throttled,
    _get_usb_errors,
    _run,
    log_system_metrics,
)


# ---------------------------------------------------------------------------
# _run
# ---------------------------------------------------------------------------


def test_run_returns_stripped_output_on_success(monkeypatch):
    monkeypatch.setattr(
        subprocess, "check_output", lambda cmd, text, timeout: "  hello  \n"
    )
    assert _run(["echo", "hello"]) == "hello"


@pytest.mark.parametrize(
    "raised_exception",
    [
        subprocess.CalledProcessError(1, "cmd"),
        subprocess.TimeoutExpired("cmd", 5),
        FileNotFoundError("no such file"),
        PermissionError("permission denied"),
    ],
)
def test_run_returns_empty_string_and_logs_warning_on_failure(
    monkeypatch, caplog, raised_exception
):
    def fake_check_output(cmd, text, timeout):
        raise raised_exception

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    with caplog.at_level(logging.WARNING, logger="django"):
        result = _run(["some", "cmd"])

    assert result == ""
    assert "Command failed" in caplog.text


# ---------------------------------------------------------------------------
# _decode_throttled
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected_now, expected_since_boot",
    [
        ("throttled=0x0", "ok", "ok"),
        ("throttled=0x1", "under-voltage", "ok"),
        ("throttled=0x4", "throttled", "ok"),
        (
            "throttled=0xf",
            "under-voltage,arm freq capped,throttled,soft temp limit",
            "ok",
        ),
        ("throttled=0x10000", "ok", "under-voltage"),
        ("throttled=0x50000", "ok", "under-voltage,throttled"),
        ("throttled=0x50001", "under-voltage", "under-voltage,throttled"),
        # malformed input
        ("", "unknown", "unknown"),
        ("garbage", "unknown", "unknown"),
        ("throttled=zzz", "unknown", "unknown"),
    ],
)
def test_decode_throttled(raw, expected_now, expected_since_boot):
    assert _decode_throttled(raw) == (expected_now, expected_since_boot)


# ---------------------------------------------------------------------------
# _get_usb_errors
# ---------------------------------------------------------------------------


def test_get_usb_errors_returns_empty_string_when_no_dmesg_output(monkeypatch):
    monkeypatch.setattr(system_metrics, "_run", lambda cmd: "")
    assert _get_usb_errors() == ""


def test_get_usb_errors_filters_non_usb_lines(monkeypatch):
    dmesg_output = "\n".join(
        [
            "[Mon Jan  1 00:00:00 2026] some kernel line",
            "[Mon Jan  1 00:00:01 2026] usb 1-1: device disconnected",
            "[Mon Jan  1 00:00:02 2026] another unrelated line",
        ]
    )
    monkeypatch.setattr(system_metrics, "_run", lambda cmd: dmesg_output)
    assert _get_usb_errors() == "[Mon Jan  1 00:00:01 2026] usb 1-1: device disconnected"


def test_get_usb_errors_keeps_only_last_five_lines(monkeypatch):
    lines = [f"[Mon Jan  1 00:00:0{i} 2026] usb 1-1: error {i}" for i in range(7)]
    monkeypatch.setattr(system_metrics, "_run", lambda cmd: "\n".join(lines))
    result = _get_usb_errors()
    assert result == " | ".join(lines[-5:])


def test_get_usb_errors_uses_the_expected_dmesg_window(monkeypatch):
    captured_cmd = {}

    def fake_run(cmd):
        captured_cmd["cmd"] = cmd
        return ""

    monkeypatch.setattr(system_metrics, "_run", fake_run)
    _get_usb_errors()
    assert captured_cmd["cmd"] == ["dmesg", "-T", "--since", USB_DMESG_WINDOW]


# ---------------------------------------------------------------------------
# log_system_metrics
# ---------------------------------------------------------------------------


def _fake_run_factory(overrides: dict[str, str]):
    """Build a fake `_run` that returns per-command canned output, "" by default."""

    def fake_run(cmd):
        return overrides.get(cmd[0], "")

    return fake_run


def test_log_system_metrics_logs_info_when_everything_is_fine(monkeypatch, caplog):
    monkeypatch.setattr(
        system_metrics,
        "_run",
        _fake_run_factory(
            {
                "vcgencmd": "throttled=0x0",  # matches both measure_temp and get_throttled calls
                "free": "Mem: total used free\nMem: 1000 200 800",
                "df": "Filesystem Size Used Avail Use% Mounted\n/dev/root 10G 2G 8G 20% /",
                "cat": "0.10 0.05 0.01 1/200 12345",
                "uptime": "2026-07-19 08:00:00",
            }
        ),
    )
    monkeypatch.setattr(system_metrics, "_get_usb_errors", lambda: "")

    with caplog.at_level(logging.INFO, logger="django"):
        log_system_metrics()

    assert not any(record.levelno == logging.WARNING for record in caplog.records)
    assert any(record.levelno == logging.INFO for record in caplog.records)
    assert "throttled_now=ok" in caplog.text
    assert "throttled_since_boot=ok" in caplog.text


def test_log_system_metrics_logs_warning_when_throttled_now(monkeypatch, caplog):
    monkeypatch.setattr(
        system_metrics,
        "_run",
        _fake_run_factory({"vcgencmd": "throttled=0x1"}),
    )
    monkeypatch.setattr(system_metrics, "_get_usb_errors", lambda: "")

    with caplog.at_level(logging.INFO, logger="django"):
        log_system_metrics()

    assert any(record.levelno == logging.WARNING for record in caplog.records)
    assert "throttled_now=under-voltage" in caplog.text


def test_log_system_metrics_logs_info_when_only_since_boot_flag_is_set(monkeypatch, caplog):
    # Regression test: a flag that only fired once since boot shouldn't trigger
    # a warning on every single run, only an active (now) condition should.
    monkeypatch.setattr(
        system_metrics,
        "_run",
        _fake_run_factory({"vcgencmd": "throttled=0x10000"}),
    )
    monkeypatch.setattr(system_metrics, "_get_usb_errors", lambda: "")

    with caplog.at_level(logging.INFO, logger="django"):
        log_system_metrics()

    assert not any(record.levelno == logging.WARNING for record in caplog.records)
    assert "throttled_since_boot=under-voltage" in caplog.text


def test_log_system_metrics_logs_warning_when_usb_errors_present(monkeypatch, caplog):
    monkeypatch.setattr(
        system_metrics,
        "_run",
        _fake_run_factory({"vcgencmd": "throttled=0x0"}),
    )
    monkeypatch.setattr(
        system_metrics, "_get_usb_errors", lambda: "usb 1-1: device disconnected"
    )

    with caplog.at_level(logging.INFO, logger="django"):
        log_system_metrics()

    assert any(record.levelno == logging.WARNING for record in caplog.records)
    assert "usb_errors=[usb 1-1: device disconnected]" in caplog.text
