import logging
import sys
from unittest.mock import MagicMock

import pytest
from core.utils import systemd_utils


@pytest.mark.parametrize("is_development", [True, False])
def test_notify_watchdog_calls_daemon_notify_only_outside_development(monkeypatch, is_development):
    monkeypatch.setattr(systemd_utils, "environment_is_development", lambda: is_development)
    fake_systemd = MagicMock()
    monkeypatch.setitem(sys.modules, "systemd", fake_systemd)

    systemd_utils.notify_watchdog()

    if is_development:
        fake_systemd.daemon.notify.assert_not_called()
    else:
        fake_systemd.daemon.notify.assert_called_once_with("WATCHDOG=1")


def test_notify_watchdog_logs_error_when_systemd_package_missing(monkeypatch, caplog):
    monkeypatch.setattr(systemd_utils, "environment_is_development", lambda: False)
    # Setting a module to None in sys.modules forces Python's import machinery
    # to raise ImportError, simulating the systemd package not being installed.
    monkeypatch.setitem(sys.modules, "systemd", None)

    with caplog.at_level(logging.ERROR, logger="django"):
        systemd_utils.notify_watchdog()

    assert "[Systemd] ImportError" in caplog.text


def test_notify_watchdog_does_not_raise_when_systemd_package_missing(monkeypatch):
    monkeypatch.setattr(systemd_utils, "environment_is_development", lambda: False)
    monkeypatch.setitem(sys.modules, "systemd", None)

    systemd_utils.notify_watchdog()  # should not raise
