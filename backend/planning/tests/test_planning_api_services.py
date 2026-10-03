from datetime import date

import pytest

from planning.api.services import (
    build_ai_equipment_duplication_recap,
    make_equipment_key,
    parse_equipment_key,
    validate_ai_equipment_duplication_request,
    validate_duplication_period,
)

TODAY = date(2026, 8, 15)  # Saturday

# ------------------------------------------------------------------------------
# Tests for make_equipment_key / parse_equipment_key
# ------------------------------------------------------------------------------


def test_equipment_key_round_trip():
    key = make_equipment_key("water_heater", 12)

    assert key == "water_heater:12"
    assert parse_equipment_key(key) == ("water_heater", 12)


@pytest.mark.parametrize(
    "key",
    ["", "water_heater", ":1", "water_heater:", "water_heater:abc", "water_heater:-1"],
)
def test_parse_equipment_key_returns_none_if_malformed(key):
    assert parse_equipment_key(key) is None


# ------------------------------------------------------------------------------
# Tests for validate_duplication_period
# ------------------------------------------------------------------------------


def test_period_ok():
    result = validate_duplication_period([2], "2026-08-16", "2026-08-30", TODAY)

    assert result == {"status": "ok", "message": "", "nb_days_impacted": 2}


def test_period_start_today_is_accepted():
    result = validate_duplication_period([5], "2026-08-15", "2026-08-30", TODAY)

    assert result["status"] == "ok"


def test_period_warning_above_threshold():
    # Every day for ~2 months -> well above the 30 days threshold
    result = validate_duplication_period(
        [0, 1, 2, 3, 4, 5, 6], "2026-08-16", "2026-10-31", TODAY
    )

    assert result["status"] == "warning"
    assert result["nb_days_impacted"] > 30
    assert str(result["nb_days_impacted"]) in result["message"]


@pytest.mark.parametrize(
    "weekdays, start, end, expected_message_part",
    [
        ([], "2026-08-16", "2026-08-30", "Aucun jour de la semaine"),
        ([2, 2], "2026-08-16", "2026-08-30", "dupliqués"),
        ([7], "2026-08-16", "2026-08-30", "invalide"),
        ([-1], "2026-08-16", "2026-08-30", "invalide"),
        ([2], "not-a-date", "2026-08-30", "Date de début invalide"),
        ([2], "2026-08-16", "not-a-date", "Date de fin invalide"),
        ([2], "2026-08-14", "2026-08-30", "aujourd'hui ou une date future"),
        ([2], "2026-08-30", "2026-08-16", "postérieure ou égale"),
        ([2], "2026-08-16", "2028-08-16", "dépasse le maximum"),
        # Wednesday requested but the period only covers a Sunday
        ([2], "2026-08-16", "2026-08-16", "Aucun jour de la période"),
    ],
)
def test_period_errors(weekdays, start, end, expected_message_part):
    result = validate_duplication_period(weekdays, start, end, TODAY)

    assert result["status"] == "error"
    assert expected_message_part in result["message"]
    assert result["nb_days_impacted"] == 0


# ------------------------------------------------------------------------------
# Tests for validate_ai_equipment_duplication_request
# ------------------------------------------------------------------------------

KNOWN_KEYS = {"water_heater:1", "water_heater:2"}


def test_equipment_request_ok():
    result = validate_ai_equipment_duplication_request(
        ["water_heater:1"], [2], "2026-08-16", "2026-08-30", KNOWN_KEYS, TODAY
    )

    assert result["status"] == "ok"
    assert result["nb_days_impacted"] == 2


@pytest.mark.parametrize(
    "equipment_keys, expected_message_part",
    [
        ([], "Aucun équipement"),
        (["water_heater:1", "water_heater:1"], "dupliqués"),
        (["water_heater:1", "water_heater:99"], "non proposés"),
    ],
)
def test_equipment_request_selection_errors(equipment_keys, expected_message_part):
    result = validate_ai_equipment_duplication_request(
        equipment_keys, [2], "2026-08-16", "2026-08-30", KNOWN_KEYS, TODAY
    )

    assert result["status"] == "error"
    assert expected_message_part in result["message"]


def test_equipment_request_period_errors_are_propagated():
    result = validate_ai_equipment_duplication_request(
        ["water_heater:1"], [], "2026-08-16", "2026-08-30", KNOWN_KEYS, TODAY
    )

    assert result["status"] == "error"
    assert "Aucun jour de la semaine" in result["message"]


# ------------------------------------------------------------------------------
# Tests for build_ai_equipment_duplication_recap
# ------------------------------------------------------------------------------

SOURCE_DATE = date(2026, 8, 15)  # Saturday


def test_recap_all_equipments_single_weekday():
    names = {"water_heater:1": "Cumulus", "water_heater:2": "Ballon"}

    recap = build_ai_equipment_duplication_recap(
        SOURCE_DATE,
        ["water_heater:1", "water_heater:2"],
        [2],
        date(2026, 8, 16),
        date(2026, 8, 30),
        names,
    )

    assert recap == (
        "Je récapitule, vous voulez copier les plannings de tous les équipements "
        "du samedi 15 août 2026 sur tous les mercredis entre le mercredi 19 août 2026 "
        "et le mercredi 26 août 2026 ?"
    )


def test_recap_single_equipment_uses_its_name():
    names = {"water_heater:1": "Cumulus", "water_heater:2": "Ballon"}

    recap = build_ai_equipment_duplication_recap(
        SOURCE_DATE, ["water_heater:1"], [2], date(2026, 8, 16), date(2026, 8, 30), names
    )

    assert "copier le planning de Cumulus du" in recap


def test_recap_several_but_not_all_equipments_are_listed_by_name():
    names = {
        "water_heater:1": "Cumulus",
        "water_heater:2": "Ballon",
        "water_heater:3": "Cuve",
    }

    recap = build_ai_equipment_duplication_recap(
        SOURCE_DATE,
        ["water_heater:1", "water_heater:2"],
        [2],
        date(2026, 8, 16),
        date(2026, 8, 30),
        names,
    )

    assert "copier les plannings de Cumulus et Ballon du" in recap


def test_recap_all_weekdays():
    names = {"water_heater:1": "Cumulus"}

    recap = build_ai_equipment_duplication_recap(
        SOURCE_DATE,
        ["water_heater:1"],
        [0, 1, 2, 3, 4, 5, 6],
        date(2026, 8, 16),
        date(2026, 8, 23),
        names,
    )

    assert "sur tous les jours entre le dimanche 16 août 2026" in recap
    assert recap.endswith("et le dimanche 23 août 2026 ?")


def test_recap_uses_effective_first_and_last_occurrences():
    """The period is Aug 16 -> Aug 30 but with Wed+Thu the first/last matching days are
    Wed Aug 19 and Thu Aug 27, and those are what the recap must announce."""
    names = {"water_heater:1": "Cumulus"}

    recap = build_ai_equipment_duplication_recap(
        SOURCE_DATE,
        ["water_heater:1"],
        [2, 3],
        date(2026, 8, 16),
        date(2026, 8, 30),
        names,
    )

    assert "sur tous les mercredis et jeudis" in recap
    assert "entre le mercredi 19 août 2026 et le jeudi 27 août 2026" in recap
