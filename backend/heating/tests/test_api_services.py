from datetime import date, timedelta
from unittest.mock import patch

import pytest
from heating.api.constants import DayStatus
from heating.api.services import add_day_status, group_slots_hashes_by_date

DEFAULT_DATE_1 = date(2025, 12, 9)
DEFAULT_DATE_2 = date(2025, 12, 10)

HASH_1 = "slots_hash_1"
HASH_2 = "slots_hash_2"
HASH_3 = "slots_hash_3"
SLOTS_HASHES = [
    (DEFAULT_DATE_1, HASH_1),
    (DEFAULT_DATE_1, HASH_2),
    (DEFAULT_DATE_2, HASH_3),
]


def test_group_slots_hashes_by_date_normal_case():
    result = group_slots_hashes_by_date(SLOTS_HASHES)
    assert result == {DEFAULT_DATE_1: {HASH_1, HASH_2}, DEFAULT_DATE_2: {HASH_3}}


@pytest.mark.parametrize(
    "slots_hashes, result",
    [
        ([], {}),
        (None, {}),
        (date(2025, 1, 1), {}),
        (False, {}),
        ([1, 2], {}),
        ({}, {}),
    ],
)
def test_group_slots_hashes_by_date_other_cases(slots_hashes, result):
    assert group_slots_hashes_by_date(slots_hashes) == result


def test_add_day_status_normal_case():
    heating_calendar = [
        # have heating plans
        {"date": date(2025, 12, 9), "status": DayStatus.EMPTY},
        # have heating plans
        {"date": date(2025, 12, 10), "status": DayStatus.EMPTY},
        # don't have heating plans
        {"date": date(2025, 12, 11), "status": DayStatus.EMPTY},
    ]
    slots_hashes = [
        ## -------------------------
        # day one week before 2025-12-9 same hashes
        (date(2025, 12, 9) - timedelta(weeks=1), HASH_1),
        (date(2025, 12, 9) - timedelta(weeks=1), HASH_2),
        # 2025-12-9 should be Normal because all hash are identical
        (date(2025, 12, 9), HASH_1),
        (date(2025, 12, 9), HASH_2),
        ## -------------------------
        # day one week before 2025-12-10
        (date(2025, 12, 10) - timedelta(weeks=1), HASH_2),
        # 2025-12-10 should be different because hash are different
        (date(2025, 12, 10), HASH_3),
        ## -------------------------
        # day one week before 2025-12-11
        (date(2025, 12, 11) - timedelta(weeks=1), HASH_1),
    ]

    with (
        patch("heating.api.services.get_slots_hashes", return_value=slots_hashes),
    ):
        add_day_status(heating_calendar)

        assert heating_calendar == [
            {"date": date(2025, 12, 9), "status": DayStatus.NORMAL},
            {"date": date(2025, 12, 10), "status": DayStatus.DIFFERENT},
            {"date": date(2025, 12, 11), "status": DayStatus.EMPTY},
        ]


@pytest.mark.parametrize(
    "raw_heating_calendar, slots_hashes, heating_calendar",
    [
        ([{"unknow": date(2025, 12, 9), "status": DayStatus.EMPTY}], [], []),
        ([{"date": 1, "status": DayStatus.EMPTY}], [], []),
        (
            [
                {"date": date(2025, 12, 11), "status": DayStatus.EMPTY},
                {"unknow": date(2025, 12, 11), "status": DayStatus.EMPTY},
            ],
            [],
            [],
        ),
        (None, [], []),
        ([], [], []),
    ],
)
def test_add_day_status_return_empty_list(
    raw_heating_calendar, slots_hashes, heating_calendar
):
    with (
        patch("heating.api.services.get_slots_hashes", return_value=slots_hashes),
    ):
        assert add_day_status(raw_heating_calendar) == heating_calendar
