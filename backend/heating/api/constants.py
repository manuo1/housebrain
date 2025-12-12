from enum import StrEnum


class DayStatus(StrEnum):
    EMPTY = "empty"
    NORMAL = "normal"
    DIFFERENT = "different"


class DuplicationTypes(StrEnum):
    WEEK = "week"
    DAY = "day"
