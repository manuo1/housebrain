import logging
import serial
import threading
import time
from core.utils import colored_text
from teleinfo.services import (
    buffer_can_accept_new_data,
    get_data_in_line,
    buffer_is_complete,
)
from core.constants import LoggerLabel, TerminalColor
from teleinfo.constants import SerialConfig
from django.utils import timezone

logger = logging.getLogger("django")


class TeleinfoListener:
    def __init__(self) -> None:
        self.buffer = {}
        self.teleinfo = {}
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._listen, daemon=True)

    def start(self) -> None:
        """Starts the listener thread."""
        if not self._thread.is_alive():
            self._stop_event.clear()
            self._thread.start()
            logger.info(f"{LoggerLabel.TELEINFOLISTENER} Thread started.")
        else:
            logger.warning(
                f"{LoggerLabel.TELEINFOLISTENER} Listener is already running."
            )

    def stop(self) -> None:
        """Stops the listener thread."""
        if self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            logger.info(f"{LoggerLabel.TELEINFOLISTENER} Thread stopped.")

    def _listen(self) -> None:
        """Internal method to listen for incoming teleinfo data."""
        try:
            with serial.Serial(
                port=SerialConfig.PORT.value,
                baudrate=SerialConfig.BAUDRATE.value,
                parity=SerialConfig.PARITY.value,
                stopbits=SerialConfig.STOPBITS.value,
                bytesize=SerialConfig.BYTESIZE.value,
                timeout=SerialConfig.TIMEOUT.value,
            ) as serial_connection:

                while not self._stop_event.is_set():
                    self._fetch_data(serial_connection)
        except serial.SerialException as e:
            logger.error(f"{LoggerLabel.TELEINFOLISTENER} Cannot open serial port: {e}")
            time.sleep(5)

    def _fetch_data(self, connection: serial.Serial) -> None:
        """Fetch data from the serial connection."""
        try:
            if connection.in_waiting:
                self._process_data(connection.readline())
            else:
                logger.warning(
                    f"{LoggerLabel.TELEINFOLISTENER} No data received, retrying..."
                )
                time.sleep(1)
        except serial.SerialException as e:
            logger.error(f"{LoggerLabel.TELEINFOLISTENER} Serial error: {e}")
            time.sleep(2)

    def _process_data(self, raw_data: bytes) -> None:
        """Process the incoming raw data line."""
        key, value = get_data_in_line(raw_data)
        if buffer_can_accept_new_data(key, self.buffer):
            self.buffer[key] = value
        if buffer_is_complete(self.buffer):
            self.teleinfo = self.buffer.copy()
            self.teleinfo.update({"created": timezone.now(), "last_save": None})
            self.buffer.clear()
            logger.info(
                colored_text(
                    f"{LoggerLabel.TELEINFOLISTENER} Teleinfo : {self.teleinfo}",
                    TerminalColor.CYAN,
                )
            )
