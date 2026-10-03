from datetime import date, timedelta
from unittest.mock import patch

import pytest

from heating.api.constants import DayStatus
from heating.api.services import (
    add_day_status,
    build_ai_duplication_recap,
    group_slots_hashes_by_date,
    validate_ai_duplication_request,
)
from rooms.tests.factories import RoomFactory

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


# ------------------------------------------------------------------------------
# Tests for validate_ai_duplication_request
# ------------------------------------------------------------------------------

TODAY = date(2026, 8, 15)
KNOWN_ROOM_IDS = {1, 2, 3, 4}


def test_validate_ai_duplication_request_ok():
    result = validate_ai_duplication_request(
        [1, 2], [0, 2], "2026-08-16", "2026-08-19", KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "ok"
    assert result["message"] == ""
    assert result["nb_days_impacted"] == 2  # Monday 17 + Wednesday 19


def test_validate_ai_duplication_request_warning_above_threshold():
    # every day for 60 days > threshold (30)
    result = validate_ai_duplication_request(
        [1], [0, 1, 2, 3, 4, 5, 6], "2026-08-16", "2026-10-15", KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "warning"
    assert "confirmez-vous" in result["message"]
    assert result["nb_days_impacted"] > 30


def test_validate_ai_duplication_request_start_today_is_allowed():
    # today is not over yet, its plan can still be duplicated onto
    result = validate_ai_duplication_request(
        [1],
        [TODAY.weekday()],
        TODAY.isoformat(),
        TODAY.isoformat(),
        KNOWN_ROOM_IDS,
        TODAY,
    )
    assert result["status"] == "ok"
    assert result["nb_days_impacted"] == 1


def test_validate_ai_duplication_request_source_date_in_future_start_before_it_is_allowed():
    # start only needs to be >= today, it may be before a future source_date
    result = validate_ai_duplication_request(
        [1], [0], "2026-08-17", "2026-08-17", KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "ok"


@pytest.mark.parametrize(
    "room_ids, weekdays, start, end, expected_message_snippet",
    [
        ([], [0], "2026-08-16", "2026-08-20", "Aucune pièce"),
        ([1, 1], [0], "2026-08-16", "2026-08-20", "pièces sont dupliquées"),
        ([1, 99], [0], "2026-08-16", "2026-08-20", "non proposées"),
        ([1], [], "2026-08-16", "2026-08-20", "Aucun jour"),
        ([1], [0, 0], "2026-08-16", "2026-08-20", "jours de la semaine sont dupliqués"),
        ([1], [7], "2026-08-16", "2026-08-20", "invalide"),
        ([1], [-1], "2026-08-16", "2026-08-20", "invalide"),
        ([1], [0], "not-a-date", "2026-08-20", "début invalide"),
        ([1], [0], "2026-08-16", "not-a-date", "fin invalide"),
        ([1], [0], "2026-08-14", "2026-08-20", "aujourd'hui ou une date future"),
        ([1], [0], "2026-08-20", "2026-08-16", "postérieure ou égale"),
        ([1], [0], "2026-08-16", "2028-08-16", "dépasse le maximum"),
        # start/end range has no Sunday at all
        ([1], [6], "2026-08-17", "2026-08-19", "ne correspond aux jours"),
    ],
)
def test_validate_ai_duplication_request_errors(
    room_ids, weekdays, start, end, expected_message_snippet
):
    result = validate_ai_duplication_request(
        room_ids, weekdays, start, end, KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "error"
    assert result["nb_days_impacted"] == 0
    assert expected_message_snippet in result["message"]


# ------------------------------------------------------------------------------
# Tests for build_ai_duplication_recap
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_build_ai_duplication_recap_all_rooms_single_weekday():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")
    all_room_ids = {room_a.id, room_b.id}

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),  # Saturday
        [room_a.id, room_b.id],
        [2],  # Wednesday
        date(2026, 8, 16),
        date(2026, 8, 30),
        all_room_ids,
    )

    assert recap == (
        "Je récapitule, vous voulez copier les plannings de toutes les pièces "
        "du samedi 15 août 2026 sur tous les mercredi "
        "entre le mercredi 19 août 2026 et le mercredi 26 août 2026 ?"
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_single_room_single_weekday():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id],
        [2],
        date(2026, 8, 16),
        date(2026, 8, 30),
        {room_a.id, room_b.id},
    )

    assert recap == (
        "Je récapitule, vous voulez copier le planning de Chambre P "
        "du samedi 15 août 2026 sur tous les mercredi "
        "entre le mercredi 19 août 2026 et le mercredi 26 août 2026 ?"
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_two_rooms_two_weekdays():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre d'amis")
    room_c = RoomFactory(name="Cuisine")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id, room_b.id],
        [2, 3],  # Wednesday, Thursday
        date(2026, 8, 16),
        date(2026, 8, 30),
        {room_a.id, room_b.id, room_c.id},
    )

    assert recap == (
        "Je récapitule, vous voulez copier les plannings de Chambre P et Chambre d'amis "
        "du samedi 15 août 2026 sur tous les mercredi et jeudi "
        "entre le mercredi 19 août 2026 et le jeudi 27 août 2026 ?"
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_three_rooms_three_weekdays():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")
    room_c = RoomFactory(name="Chambre M")
    room_d = RoomFactory(name="Cuisine")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id, room_b.id, room_c.id],
        [0, 2, 4],  # Monday, Wednesday, Friday
        date(2026, 8, 16),
        date(2026, 9, 15),
        {room_a.id, room_b.id, room_c.id, room_d.id},
    )

    assert recap.startswith(
        "Je récapitule, vous voulez copier les plannings de Chambre P, Chambre R et Chambre M "
        "du samedi 15 août 2026 sur tous les lundi, mercredi et vendredi "
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_all_weekdays():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id],
        [0, 1, 2, 3, 4, 5, 6],
        date(2026, 8, 16),
        date(2026, 8, 23),
        {room_a.id, room_b.id},
    )

    assert recap == (
        "Je récapitule, vous voulez copier le planning de Chambre P "
        "du samedi 15 août 2026 sur tous les jours "
        "entre le dimanche 16 août 2026 et le dimanche 23 août 2026 ?"
    )
