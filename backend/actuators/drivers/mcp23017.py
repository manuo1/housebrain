"""
Driver to control MCP23017 via I2C
"""

import logging

import board
import busio
from actuators.constants import MCP23017PinState
from adafruit_mcp230xx.mcp23017 import MCP23017
from core.constants import UNPLUGGED_MODE, LoggerLabel

logger = logging.getLogger("django")


class MCP23017Error(Exception):
    """Exception for MCP23017 driver errors"""

    def __init__(self, message, pin_state=MCP23017PinState.UNDEFINED):
        super().__init__(message)
        self.pin_state = pin_state  # MCP23017PinState enum


class MCP23017Driver:
    """Driver to control MCP23017 pins"""

    def __init__(self):
        self.mcp = None
        self.i2c = None
        self._connect()

    def _connect(self):
        """Initialize I2C connection and MCP23017"""
        if UNPLUGGED_MODE:
            logger.info(f"{LoggerLabel.MCPDRIVER}UNPLUGGED mode: MCP23017 simulation")
            return

        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.mcp = MCP23017(self.i2c)
            logger.debug(f"{LoggerLabel.MCPDRIVER} MCP23017 connected successfully")
        except ValueError as e:
            logger.error(f"{LoggerLabel.MCPDRIVER} I2C connection error: {e}")
            self.i2c = None
            self.mcp = None

    def _ensure_connection(self):
        """Check connection, try to reconnect if necessary"""
        if UNPLUGGED_MODE:
            return

        if self.mcp is None:
            self._connect()
            if self.mcp is None:
                raise MCP23017Error("Unable to connect to MCP23017")

    def set_pin(self, pin_number: int, state: bool):
        """
        Change pin state and verify the result

        Args:
            pin_number: Pin number (0-15)
            state: True for ON, False for OFF

        Raises:
            MCP23017Error: On error with pin state details
        """
        if UNPLUGGED_MODE:
            logger.debug(
                f"{LoggerLabel.MCPDRIVER} UNPLUGGED mode: set_pin({pin_number}, {state})"
            )
            return

        self._ensure_connection()

        try:
            # Set pin state
            mcp_pin = self.mcp.get_pin(pin_number)
            mcp_pin.switch_to_output(value=state)

            # Verify that the state was applied correctly
            actual_state = self.get_pin(pin_number)

            if actual_state != state:
                pin_state_str = (
                    MCP23017PinState.ON if actual_state else MCP23017PinState.OFF
                )
                requested_state_str = (
                    MCP23017PinState.ON if state else MCP23017PinState.OFF
                )
                raise MCP23017Error(
                    f"Pin {pin_number} state incorrect: requested {requested_state_str}, actual state {pin_state_str}",
                    pin_state=pin_state_str,
                )

            logger.debug(
                f"{LoggerLabel.MCPDRIVER} Pin {pin_number} set to {'ON' if state else 'OFF'}"
            )

        except ValueError as e:
            # MCP23017 error (invalid pin, etc.)
            raise MCP23017Error(f"MCP23017 error on pin {pin_number}: {e}")
        except Exception as e:
            # I2C or other error
            if "I2C" in str(e) or "communication" in str(e).lower():
                raise MCP23017Error(f"I2C communication error: {e}")
            else:
                raise MCP23017Error(f"Unexpected error on pin {pin_number}: {e}")

    def get_pin(self, pin_number: int) -> bool:
        """
        Read current pin state

        Args:
            pin_number: Pin number (0-15)

        Returns:
            bool: True if ON, False if OFF

        Raises:
            MCP23017Error: On read error
        """
        if UNPLUGGED_MODE:
            logger.debug(
                f"{LoggerLabel.MCPDRIVER} UNPLUGGED mode: get_pin({pin_number}) -> False"
            )
            return False

        self._ensure_connection()

        try:
            mcp_pin = self.mcp.get_pin(pin_number)
            state = mcp_pin.value
            logger.debug(
                f"{LoggerLabel.MCPDRIVER} Pin {pin_number} state: {'ON' if state else 'OFF'}"
            )
            return state

        except ValueError as e:
            # MCP23017 error (invalid pin, etc.)
            raise MCP23017Error(f"MCP23017 error on pin {pin_number}: {e}")
        except Exception as e:
            # I2C or other error
            if "I2C" in str(e) or "communication" in str(e).lower():
                raise MCP23017Error(f"I2C communication error: {e}")
            else:
                raise MCP23017Error(f"Unexpected error reading pin {pin_number}: {e}")

    def get_all_pins_state(self) -> dict[int, dict]:
        """
        Return a dict with pin number as key and state/error as value:
        {
            0: {"state": MCP23017PinState.ON, "error": None},
            1: {"state": MCP23017PinState.OFF, "error": None},
            2: {"state": MCP23017PinState.UNDEFINED, "error": "I2C error"},
            ...
        }
        """
        pins_state: dict[int, dict] = {}

        for pin in range(16):
            try:
                pin_value = self.get_pin(pin)
                state = MCP23017PinState.ON if pin_value else MCP23017PinState.OFF
                pins_state[pin] = {"state": state, "error": None}
            except Exception as e:
                pins_state[pin] = {
                    "state": MCP23017PinState.UNDEFINED,
                    "error": str(e),
                }

        return pins_state


# Global driver instance (singleton)
_mcp_driver = None


def get_mcp_driver() -> MCP23017Driver:
    """Return the unique MCP23017 driver instance"""
    global _mcp_driver
    if _mcp_driver is None:
        _mcp_driver = MCP23017Driver()
    return _mcp_driver
