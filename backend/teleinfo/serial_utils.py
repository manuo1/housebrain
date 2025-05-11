import logging
import serial
from core.utils import colored_text
from core.constants import TerminalColor
from teleinfo.constants import SerialConfig

logger = logging.getLogger("django")


def get_serial_connection(config: SerialConfig) -> serial.Serial | None:
    """
    Attempts to open the serial port and returns the serial object if data is received.
    Returns a serial.Serial object if data is received, None otherwise.
    """
    try:
        with serial.Serial(config.PORT, config.BAUDRATE, timeout=config.TIMEOUT) as ser:
            data = ser.readline().decode("ascii", errors="ignore").strip()

            if data:
                logger.info(
                    colored_text(
                        f"Received data on port {config.PORT}: {data}",
                        TerminalColor.GREEN,
                    )
                )
                return ser
            else:
                logger.error(
                    colored_text(
                        f"No data received on port {config.PORT}",
                        TerminalColor.RED,
                    )
                )
                return None
    except serial.SerialException as e:
        logger.error(
            colored_text(
                f"Error opening serial port {config.PORT}: {e}",
                TerminalColor.RED,
            )
        )
        return None
