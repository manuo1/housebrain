from enum import StrEnum


class MCP23017PinState(StrEnum):
    ON = "on"
    OFF = "off"
    UNDEFINED = "undefined"


POWER_SAFETY_MARGIN = 2000  # watts
