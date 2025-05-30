from enum import StrEnum


class TerminalColor(StrEnum):
    RED = "91"
    GREEN = "92"
    YELLOW = "93"
    BLUE = "94"
    MAGENTA = "95"
    CYAN = "96"
    WHITE = "97"


DEFAULT_VOLTAGE = 220  # Volts


class LoggerLabel(StrEnum):
    TELEINFOLISTENER = "[TeleinfoListener]"
    SYSTEMD = "[Systemd]"
    PERIODIC_TASKS = "[Periodic Tasks]"
    CONSUMPTION = "[Consumption]"
