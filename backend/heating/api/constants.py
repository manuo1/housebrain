from enum import StrEnum


class DayStatus(StrEnum):
    EMPTY = "empty"
    NORMAL = "normal"
    DIFFERENT = "different"


class DuplicationTypes(StrEnum):
    WEEK = "week"
    DAY = "day"


ALL_WEEK_DAY = [0, 1, 2, 3, 4, 5, 6]
