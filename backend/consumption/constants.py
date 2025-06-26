from enum import StrEnum

ALLOWED_CONSUMPTION_STEPS = [1, 30, 60]


class ConsumptionPeriod(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


ALLOWED_CONSUMPTION_PERIODS = tuple(ConsumptionPeriod)
