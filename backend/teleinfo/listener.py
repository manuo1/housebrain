import logging
import serial
import time
from core.utils.systemd_utils import notify_watchdog
from teleinfo.services import (
    buffer_can_accept_new_data,
    get_data_in_line,
    buffer_is_complete,
)
from core.constants import LoggerLabel
from teleinfo.constants import SerialConfig
from django.utils import timezone
from django.core.cache import caches


cache = caches["default"]
logger = logging.getLogger("django")


class TeleinfoListener:
    def __init__(self) -> None:
        self.buffer = {}
        self.teleinfo = {}
        cache.set("teleinfo_data", {"last_read": None}, timeout=None)

    def start(self) -> None:
        """Starts the listener process."""
        try:
            with serial.Serial(
                port=SerialConfig.PORT.value,
                baudrate=SerialConfig.BAUDRATE.value,
                parity=SerialConfig.PARITY.value,
                stopbits=SerialConfig.STOPBITS.value,
                bytesize=SerialConfig.BYTESIZE.value,
                timeout=SerialConfig.TIMEOUT.value,
            ) as serial_connection:
                logger.info(f"{LoggerLabel.TELEINFOLISTENER} Listening for data...")

                while True:
                    self._fetch_data(serial_connection)
        except serial.SerialException as e:
            logger.error(f"{LoggerLabel.TELEINFOLISTENER} Cannot open serial port: {e}")
            time.sleep(5)

    def _fetch_data(self, connection: serial.Serial) -> None:
        """Fetch data from the serial connection."""
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
            self.teleinfo.update({"last_read": timezone.now()})
            self.buffer.clear()
            cache.set("teleinfo_data", self.teleinfo, timeout=None)
            notify_watchdog()
