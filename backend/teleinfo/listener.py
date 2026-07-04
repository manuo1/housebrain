import logging
import time

import serial
from core.constants import LoggerLabel
from core.utils.systemd_utils import notify_watchdog
from django.core.cache import caches
from django.utils import timezone
from heating.services.heating_synchronization import (
    turn_on_radiators_according_to_the_available_power,
)
from teleinfo.constants import SerialConfig
from teleinfo.services import (
    buffer_can_accept_new_data,
    buffer_is_complete,
    ensure_power_not_exceeded,
    get_data_in_line,
)
from teleinfo.utils.cache_teleinfo_data import set_teleinfo_data_in_cache

cache = caches["default"]
logger = logging.getLogger("django")


class TeleinfoListener:
    def __init__(self) -> None:
        self.buffer = {}
        self.teleinfo = {}
        self.should_manage_radiator_power = False
        self._last_watchdog_notify = time.monotonic()
        set_teleinfo_data_in_cache({"last_read": None})

    def _notify_watchdog_if_needed(self) -> None:
        now = time.monotonic()
        if now - self._last_watchdog_notify >= 10:  # every 10s
            notify_watchdog()
            self._last_watchdog_notify = now

    def start(self) -> None:
        """Starts the listener process."""
        # Retry loop for recoverable serial errors only (port not ready yet,
        # transient USB glitch). This avoids tearing down the whole Django
        # process for a hiccup that a simple reopen can fix. Any other
        # (unexpected) exception is intentionally left to propagate: it
        # kills the process and lets systemd's Restart=always take over,
        # instead of silently looping on a possibly broken state.
        while True:
            # Ping the watchdog right before the blocking serial.Serial()
            # call. Without this, no ping is sent between process startup
            # and the end of the port opening: if that takes longer than
            # WatchdogSec (seen right after a reboot, when the USB-serial
            # device isn't fully stable yet), systemd kills the process
            # thinking it's stuck.
            notify_watchdog()
            try:
                with serial.Serial(
                    port=SerialConfig.PORT.value,
                    baudrate=SerialConfig.BAUDRATE.value,
                    parity=SerialConfig.PARITY.value,
                    stopbits=SerialConfig.STOPBITS.value,
                    bytesize=SerialConfig.BYTESIZE.value,
                    timeout=SerialConfig.TIMEOUT.value,
                ) as serial_connection:
                    # Port opened successfully: restart with a full 10s
                    # window for the next ping, regardless of how long the
                    # opening took.
                    self._last_watchdog_notify = time.monotonic()
                    notify_watchdog()
                    logger.info(f"{LoggerLabel.TELEINFOLISTENER} Listening for data...")

                    while True:
                        self._fetch_data(serial_connection)
            except serial.SerialException as e:
                logger.error(
                    f"{LoggerLabel.TELEINFOLISTENER} Cannot open serial port: {e}"
                )
                # Notify before sleeping so this wait doesn't add to a
                # watchdog window already in progress before the exception.
                notify_watchdog()
                time.sleep(5)

    def _fetch_data(self, connection: serial.Serial) -> None:
        """Fetch data from the serial connection."""
        self._notify_watchdog_if_needed()
        try:
            if connection.in_waiting:
                self._process_data(connection.readline())
        except serial.SerialException as e:
            logger.error(f"{LoggerLabel.TELEINFOLISTENER} Serial error: {e}")
            time.sleep(2)

    def _process_data(self, raw_data: bytes) -> None:
        """Process the incoming raw data line."""
        key, value = get_data_in_line(raw_data)

        if buffer_can_accept_new_data(key, self.buffer):
            self.buffer[key] = value
        if buffer_is_complete(self.buffer):
            self.teleinfo.clear()
            self.teleinfo = self.buffer.copy()
            self.teleinfo.update({"last_read": timezone.now().isoformat()})
            self.buffer.clear()
            set_teleinfo_data_in_cache(self.teleinfo)
            # Alternate power management cycles to allow teleinfo
            # to reflect changes before applying new modifications
            if self.should_manage_radiator_power:
                ensure_power_not_exceeded()
                turn_on_radiators_according_to_the_available_power()
            self.should_manage_radiator_power = not self.should_manage_radiator_power
