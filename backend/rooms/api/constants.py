from enum import StrEnum


class ApiRadiatorState(StrEnum):
    ON = "on"
    OFF = "off"
    TURNING_ON = "turning_on"
    SHUTTING_DOWN = "shutting_down"
    LOAD_SHED = "load_shed"
    UNDEFINED = "undefined"


class TemperatureTrend(StrEnum):
    UP = "up"
    DOWN = "down"
    SAME = "same"
