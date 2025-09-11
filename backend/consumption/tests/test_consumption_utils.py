import pytest
from copy import deepcopy
from datetime import date, datetime
from consumption.constants import STEP_1MIN_DICT, STEP_30MIN_DICT, STEP_60MIN_DICT
from teleinfo.constants import (
    ISOUC_TO_SUBSCRIBED_POWER,
    TELEINFO_INDEX_LABELS,
    TarifPeriods,
    TeleinfoLabel,
)
from unittest.mock import patch


from consumption.utils import (
    add_new_tarif_period,
    add_new_values,
    compute_indexes_missing_values,
    compute_period_price,
    compute_totals_for_a_day,
    compute_watt_hours,
    downsample_indexes,
    fill_missing_values,
    find_all_missing_value_zones,
    get_daily_index_structure,
    get_cache_teleinfo_data,
    get_human_readable_index_label,
    get_human_readable_tarif_period,
    get_index_label,
    get_indexes_in_teleinfo,
    get_subscribed_power,
    get_tarif_period,
    get_tarif_period_label_from_index_label,
    get_wh_of_index_label,
    interpolate_missing_values,
    is_interpolated,
)


@pytest.mark.parametrize(
    "step, expected_dict",
    [
        (1, STEP_1MIN_DICT),
        (30, STEP_30MIN_DICT),
        (60, STEP_60MIN_DICT),
    ],
)
def test_get_daily_index_structure_valid_steps(step, expected_dict):
    result = get_daily_index_structure(step)
    assert result == expected_dict


@pytest.mark.parametrize("invalid_step", ["1", 15, 0, 61, 1.0, None, [], {}])
def test_get_daily_index_structure_invalid_steps(invalid_step):
    with pytest.raises(ValueError):
        get_daily_index_structure(invalid_step)


@pytest.mark.parametrize(
    "indexes, expected",
    [
        (
            {
                "label1": {
                    "00:00": 1000,
                    "00:01": 1005,
                    "00:02": 1010,
                    "24:00": 1020,
                },
                "label2": {
                    "00:00": 2000,
                    "00:01": 2002,
                    "00:02": 2005,
                    "24:00": 2010,
                },
            },
            {
                "label1": {
                    ("00:00", "00:01"): 5,  # 1005 - 1000
                    ("00:01", "00:02"): 5,  # 1010 - 1005
                    ("00:02", "24:00"): 10,  # 1020 - 1010
                },
                "label2": {
                    ("00:00", "00:01"): 2,  # 2002 - 2000
                    ("00:01", "00:02"): 3,  # 2005 - 2002
                    ("00:02", "24:00"): 5,  # 2010 - 2005
                },
            },
        ),
        # Case with None values
        (
            {
                "label1": {
                    "00:00": 1000,
                    "00:01": None,
                    "00:02": 1010,
                    "24:00": 1020,
                },
            },
            {
                "label1": {
                    ("00:00", "00:01"): None,  # next value None -> no subtraction
                    ("00:01", "00:02"): None,  # current value None -> skip
                    ("00:02", "24:00"): 10,  # 1020 - 1010
                },
            },
        ),
        # Case empty input
        ({}, {}),
    ],
)
def test_compute_watt_hours(indexes, expected):
    result = compute_watt_hours(indexes)
    assert result == expected


@pytest.mark.parametrize(
    "values, expected",
    [
        # Normal case
        (
            {
                "HCHP": {"00:00": 1000, "12:00": 1500, "24:00": 1600},
                "HCHC": {"00:00": 2000, "24:00": 2200},
            },
            {"Heures Pleines": 600, "Heures Creuses": 200, "Total": 800},
        ),
        # None values at the start or end
        (
            {
                "HCHP": {"00:00": None, "06:00": 1200, "24:00": 1500},
                "HCHC": {"00:00": 1200, "06:00": 1500, "24:00": None},
            },
            {"Heures Pleines": 300, "Heures Creuses": 300, "Total": 600},
        ),
        # None values at the start and end
        (
            {
                "HCHP": {"00:00": None, "06:00": 1200, "12:00": 1500, "24:00": None},
            },
            {"Heures Pleines": 300, "Total": 300},
        ),
        # Case where all values are None
        (
            {
                "HCHP": {"00:00": None, "06:00": None},
            },
            {"Heures Pleines": None, "Total": None},
        ),
        # Index don't change
        (
            {
                "HCHP": {},
                "HCHC": {"00:00": 1234, "24:00": 1234},
            },
            {"Heures Pleines": None, "Heures Creuses": 0, "Total": 0},
        ),
        # Not enough data
        (
            {
                "HCHC": {"00:00": 1234, "06:00": None, "24:00": None},
            },
            {"Heures Creuses": None, "Total": None},
        ),
        # Empty input
        (
            {},
            {"Total": None},
        ),
    ],
)
def test_compute_totals(values, expected):
    result = compute_totals_for_a_day(date(2025, 6, 24), values)
    wh_result = {label: result[label]["wh"] for label in result}
    assert wh_result == expected


@pytest.mark.parametrize(
    "data_dict, expected",
    [
        # Case with one missing zone
        (
            {
                "00:08": 100,
                "00:09": 100,
                "00:10": 100,
                "00:11": None,
                "00:12": None,
                "00:13": 120,
                "00:14": 120,
                "00:15": 120,
            },
            [
                [
                    ("00:10", 100),
                    ("00:11", None),
                    ("00:12", None),
                    ("00:13", 120),
                ]
            ],
        ),
        # Case with two missing zones
        (
            {
                "00:08": 50,
                "00:09": 50,
                "00:10": 50,
                "00:11": None,
                "00:12": 70,
                "00:13": None,
                "00:14": None,
                "00:15": 90,
                "00:16": 90,
                "00:17": 90,
            },
            [
                [
                    ("00:10", 50),
                    ("00:11", None),
                    ("00:12", 70),
                ],
                [
                    ("00:12", 70),
                    ("00:13", None),
                    ("00:14", None),
                    ("00:15", 90),
                ],
            ],
        ),
        # Case where missing values are at the beginning (no zone detected)
        (
            {
                "00:10": None,
                "00:11": None,
                "00:12": 10,
                "00:13": 20,
            },
            None,
        ),
        # Case where missing values are at the end (no zone detected)
        (
            {
                "00:10": 10,
                "00:11": 20,
                "00:12": None,
                "00:13": None,
            },
            None,
        ),
        # Case with no missing values
        (
            {
                "00:10": 1,
                "00:11": 2,
                "00:12": 3,
            },
            None,
        ),
        # Case with all values missing (no zone detected)
        (
            {
                "00:10": None,
                "00:11": None,
                "00:12": None,
            },
            None,
        ),
        # Case with texte as values
        (
            {
                "00:08": "a",
                "00:09": "a",
                "00:10": "a",
                "00:11": None,
                "00:12": None,
                "00:13": "b",
                "00:14": "b",
                "00:15": "b",
            },
            [
                [
                    ("00:10", "a"),
                    ("00:11", None),
                    ("00:12", None),
                    ("00:13", "b"),
                ]
            ],
        ),
    ],
)
def test_find_all_missing_value_zones(data_dict, expected):
    assert find_all_missing_value_zones(data_dict) == expected


@pytest.mark.parametrize(
    "zone, expected",
    [
        # Simple case: 1 missing value between 100 and 200
        (
            [
                ("00:00", 100),
                ("00:01", None),
                ("00:02", 200),
            ],
            [("00:01", 150)],
        ),
        # 2 missing values between 0 and 30 → [10, 20]
        (
            [
                ("00:00", 0),
                ("00:01", None),
                ("00:02", None),
                ("00:03", 30),
            ],
            [("00:01", 10), ("00:02", 20)],
        ),
        # Uneven division: 100 → 103, steps = [1, 1, 1]
        (
            [
                ("00:00", 100),
                ("00:01", None),
                ("00:02", None),
                ("00:03", None),
                ("00:04", 103),
            ],
            [("00:01", 101), ("00:02", 102), ("00:03", 103)],
        ),
        # Case with remainder: 0 → 10, 3 steps → [3,3,2]
        (
            [
                ("00:00", 0),
                ("00:01", None),
                ("00:02", None),
                ("00:03", None),
                ("00:04", 10),
            ],
            [("00:01", 3), ("00:02", 6), ("00:03", 8)],
        ),
        # Not enough elements to interpolate
        (
            [
                ("00:00", 10),
                ("00:01", 20),
            ],
            [("00:00", 10), ("00:01", 20)],
        ),
        # Invalid input: first or last value is None
        (
            [
                ("00:00", None),
                ("00:01", None),
                ("00:02", 100),
            ],
            [("00:00", None), ("00:01", None), ("00:02", 100)],
        ),
        (
            [
                ("00:00", 50),
                ("00:01", None),
                ("00:02", None),
                ("00:03", None),
                ("00:04", None),
                ("00:05", 70),
            ],
            [("00:01", 54), ("00:02", 58), ("00:03", 62), ("00:04", 66)],
        ),
    ],
)
def test_interpolate_missing_values(zone, expected):
    result = interpolate_missing_values(zone)
    assert result == expected


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        # Simple case: one missing value between two known values
        (
            {
                "HCHC": {
                    "00:00": 100,
                    "00:01": None,
                    "00:02": 200,
                }
            },
            {"HCHC": {"00:01": 150}},
        ),
        # Multiple missing values
        (
            {
                "HCHP": {
                    "00:00": 0,
                    "00:01": None,
                    "00:02": None,
                    "00:03": 30,
                }
            },
            {
                "HCHP": {
                    "00:01": 10,
                    "00:02": 20,
                }
            },
        ),
        # Two different labels with separate missing zones
        (
            {
                "HCHC": {
                    "00:00": 0,
                    "00:01": None,
                    "00:02": 30,
                },
                "HCHP": {
                    "00:00": 200,
                    "00:01": None,
                    "00:02": None,
                    "00:03": 260,
                },
            },
            {"HCHC": {"00:01": 15}, "HCHP": {"00:01": 220, "00:02": 240}},
        ),
        # No missing values
        (
            {
                "HCHC": {
                    "00:00": 100,
                    "00:01": 110,
                    "00:02": 120,
                }
            },
            {},
        ),
        # Zone too short for interpolation (less than 3 items)
        (
            {
                "HCHC": {
                    "00:00": None,
                    "00:01": 100,
                }
            },
            {},
        ),
        # All values are None
        (
            {
                "HCHC": {
                    "00:00": None,
                    "00:01": None,
                    "00:02": None,
                }
            },
            {},
        ),
    ],
)
def test_compute_indexes_missing_values(input_data, expected_output):
    result = compute_indexes_missing_values(deepcopy(input_data))
    assert result == expected_output


@pytest.mark.parametrize(
    "original, to_fill, expected",
    [
        # Basic interpolation on a single label
        (
            {"HCHC": {"00:00": 100, "00:01": None, "00:02": 200, "00:03": None}},
            {"HCHC": {"00:01": 150}},
            {"HCHC": {"00:00": 100, "00:01": 150, "00:02": 200, "00:03": None}},
        ),
        # Multiple labels, multiple fills
        (
            {
                "HCHC": {"00:00": 0, "00:01": None, "00:02": 30},
                "HCHP": {"00:00": 200, "00:01": None, "00:02": None, "00:03": 260},
            },
            {
                "HCHC": {"00:01": 15},
                "HCHP": {"00:01": 220, "00:02": 240},
            },
            {
                "HCHC": {"00:00": 0, "00:01": 15, "00:02": 30},
                "HCHP": {"00:00": 200, "00:01": 220, "00:02": 240, "00:03": 260},
            },
        ),
        # No missing values to fill
        (
            {"HCHC": {"00:00": 100, "00:01": 110}},
            {},
            {"HCHC": {"00:00": 100, "00:01": 110}},
        ),
        # Don't filling a time key that doesn't exist in original (should not be added)
        (
            {"HCHC": {"00:00": 100}},
            {"HCHC": {"00:01": 150}},
            {"HCHC": {"00:00": 100}},
        ),
        # Don't replace a non None value  (should not be added)
        (
            {"HCHC": {"00:00": 100}},
            {"HCHC": {"00:00": 150}},
            {"HCHC": {"00:00": 100}},
        ),
        # Basic interpolation with different type of key, values
        (
            {"HC..": {("00:00", "00:01"): None, "A": None, 2: None, "00:03": None}},
            {"HC..": {("00:00", "00:01"): 1, "A": 2, 2: 3, "00:03": 4}},
            {"HC..": {("00:00", "00:01"): 1, "A": 2, 2: 3, "00:03": 4}},
        ),
    ],
)
def test_fill_missing_values(original, to_fill, expected):
    result = fill_missing_values(deepcopy(original), deepcopy(to_fill))
    assert result == expected


@pytest.mark.parametrize(
    "indexes, step, expected",
    [
        # Step 60: ne garde que les heures pleines
        (
            {
                "label1": {
                    "00:00": 100,
                    "00:30": 150,
                    "01:00": 200,
                    "01:30": 250,
                    "02:00": 300,
                },
                "label2": {
                    "00:00": 50,
                    "00:15": 75,
                    "01:00": 100,
                    "02:00": 150,
                },
            },
            60,
            {
                "label1": {
                    "00:00": 100,
                    "01:00": 200,
                    "02:00": 300,
                },
                "label2": {
                    "00:00": 50,
                    "01:00": 100,
                    "02:00": 150,
                },
            },
        ),
        # Step 30: garde toutes les demi-heures
        (
            {
                "label1": {
                    "00:00": 10,
                    "00:15": 20,
                    "00:30": 30,
                    "00:45": 40,
                    "01:00": 50,
                }
            },
            30,
            {
                "label1": {
                    "00:00": 10,
                    "00:30": 30,
                    "01:00": 50,
                }
            },
        ),
        # Step 1: garde tout
        (
            {
                "label1": {
                    "00:00": 1,
                    "00:01": 2,
                    "00:02": 3,
                }
            },
            1,
            {
                "label1": {
                    "00:00": 1,
                    "00:01": 2,
                    "00:02": 3,
                }
            },
        ),
    ],
)
def test_downsample_indexes(indexes, step, expected):
    result = downsample_indexes(indexes, step)
    assert result == expected


def test_downsample_indexes_invalid_step():
    with pytest.raises(ValueError):
        downsample_indexes({"label": {"00:00": 100}}, step=15)


@pytest.mark.parametrize(
    "tarif_period, expected",
    [
        (TarifPeriods.TH, TeleinfoLabel.BASE),
        (TarifPeriods.HC, TeleinfoLabel.HCHC),
        (TarifPeriods.HP, TeleinfoLabel.HCHP),
        (TarifPeriods.HN, TeleinfoLabel.EJPHN),
        (TarifPeriods.PM, TeleinfoLabel.EJPHPM),
        (TarifPeriods.HCJB, TeleinfoLabel.BBRHCJB),
        (TarifPeriods.HCJW, TeleinfoLabel.BBRHCJW),
        (TarifPeriods.HCJR, TeleinfoLabel.BBRHCJR),
        (TarifPeriods.HPJB, TeleinfoLabel.BBRHPJB),
        (TarifPeriods.HPJW, TeleinfoLabel.BBRHPJW),
        (TarifPeriods.HPJR, TeleinfoLabel.BBRHPJR),
        ("UNKNOWN", None),  # invalid input (not in enum)
        (None, None),  # None input
    ],
)
def test_get_index_label(tarif_period, expected):
    assert get_index_label(tarif_period) == expected


@pytest.mark.parametrize(
    "computed_watt_hours, current_index_label, period, expected",
    [
        (
            {
                "HCHC": {("00:00", "00:01"): 5, ("00:01", "00:02"): 7},
                "HCHP": {("00:00", "00:01"): 10},
            },
            "HCHC",
            ("00:00", "00:01"),
            5,
        ),
        (
            {
                "HCHC": {("00:00", "00:01"): 5},
            },
            "HCHP",
            ("00:00", "00:01"),
            None,
        ),
        (
            {
                "HCHC": {("00:00", "00:01"): 5},
            },
            "HCHC",
            ("01:00", "02:00"),
            None,
        ),
    ],
)
def test_get_wh_of_index_label(
    computed_watt_hours, current_index_label, period, expected
):
    assert (
        get_wh_of_index_label(computed_watt_hours, current_index_label, period)
        == expected
    )


@pytest.mark.parametrize(
    "current_time_str, current_index, missing_indexes, expected",
    [
        ("00:01", "HCHC", {"HCHC": {"00:01": 123}}, True),
        ("00:02", "HCHC", {"HCHC": {"00:01": 123}}, False),
        ("00:01", "HCHP", {"HCHC": {"00:01": 123}}, False),
        ("00:01", "HCHC", {}, False),
    ],
)
def test_is_interpolated(current_time_str, current_index, missing_indexes, expected):
    assert is_interpolated(current_time_str, current_index, missing_indexes) == expected


@pytest.mark.parametrize(
    "input_period, expected",
    [
        (TarifPeriods.TH, "Toutes les Heures"),
        (TarifPeriods.HC, "Heures Creuses"),
        (TarifPeriods.HP, "Heures Pleines"),
        (TarifPeriods.HN, "Heures Normales"),
        (TarifPeriods.PM, "Heures de Pointe Mobile"),
        (TarifPeriods.HCJB, "Heures Creuses Jours Bleus"),
        (TarifPeriods.HCJW, "Heures Creuses Jours Blancs"),
        (TarifPeriods.HCJR, "Heures Creuses Jours Rouges"),
        (TarifPeriods.HPJB, "Heures Pleines Jours Bleus"),
        (TarifPeriods.HPJW, "Heures Pleines Jours Blancs"),
        (TarifPeriods.HPJR, "Heures Pleines Jours Rouges"),
        ("UNKNOWN", None),  # Test unknown key returns None
    ],
)
def test_get_human_readable_tarif_period(input_period, expected):
    assert get_human_readable_tarif_period(input_period) == expected


@pytest.mark.parametrize(
    "index_label, expected",
    [
        (TeleinfoLabel.BASE, "Toutes les Heures"),
        (TeleinfoLabel.HCHC, "Heures Creuses"),
        (TeleinfoLabel.HCHP, "Heures Pleines"),
        (TeleinfoLabel.EJPHN, "Heures Normales"),
        (TeleinfoLabel.EJPHPM, "Heures de Pointe Mobile"),
        (TeleinfoLabel.BBRHCJB, "Heures Creuses Jours Bleus"),
        (TeleinfoLabel.BBRHCJW, "Heures Creuses Jours Blancs"),
        (TeleinfoLabel.BBRHCJR, "Heures Creuses Jours Rouges"),
        (TeleinfoLabel.BBRHPJB, "Heures Pleines Jours Bleus"),
        (TeleinfoLabel.BBRHPJW, "Heures Pleines Jours Blancs"),
        (TeleinfoLabel.BBRHPJR, "Heures Pleines Jours Rouges"),
        ("UNKNOWN", None),  # Test unknown key returns None
    ],
)
def test_get_human_readable_index_label(index_label, expected):
    assert get_human_readable_index_label(index_label) == expected


@pytest.mark.parametrize(
    "cached_time, now, expected",
    [
        (
            datetime(2024, 5, 1, 10, 30),
            datetime(2024, 5, 1, 10, 30),
            {"last_read": datetime(2024, 5, 1, 10, 30), "some_data": "ok"},
        ),
        (
            datetime(2024, 5, 1, 10, 29),
            datetime(2024, 5, 1, 10, 30),
            None,
        ),
    ],
)
@patch("consumption.utils.timezone.localtime")
@patch("django.core.cache.cache.get")
def test_get_cache_teleinfo_data_valid(
    mock_cache_get, mock_localtime, cached_time, now, expected
):
    fake_data = {"last_read": cached_time, "some_data": "ok"}
    mock_cache_get.return_value = fake_data
    mock_localtime.return_value = cached_time.replace(second=0, microsecond=0)

    result = get_cache_teleinfo_data(now)
    assert result == expected


@patch("django.core.cache.cache.get")
def test_get_cache_teleinfo_data_none_last_read(mock_cache_get):
    mock_cache_get.return_value = {"last_read": None}

    result = get_cache_teleinfo_data(datetime(2024, 5, 1, 10, 30))
    assert result is None


@patch("django.core.cache.cache.get")
def test_get_cache_teleinfo_data_empty_cache(mock_cache_get):
    mock_cache_get.return_value = {}

    result = get_cache_teleinfo_data(datetime(2024, 5, 1, 10, 30))
    assert result is None


@pytest.mark.parametrize(
    "cache_data, expected",
    [
        # Cas nominal : valeur ISOUC connue
        ({TeleinfoLabel.ISOUSC: "15"}, ISOUC_TO_SUBSCRIBED_POWER["15"]),
        ({TeleinfoLabel.ISOUSC: "60"}, ISOUC_TO_SUBSCRIBED_POWER["60"]),
        # Cas erreur : ISOUC absent
        ({}, None),
        # Cas erreur : ISOUC non dans la map
        ({TeleinfoLabel.ISOUSC: "999"}, None),
        # Cas erreur : ISOUC présent mais None
        ({TeleinfoLabel.ISOUSC: None}, None),
    ],
)
def test_get_subscribed_power(cache_data, expected):
    result = get_subscribed_power(cache_data)
    assert result == expected


@pytest.mark.parametrize(
    "cache_data, expected",
    [
        # Cas nominal : PTEC présent avec différentes valeurs
        ({TeleinfoLabel.PTEC: "HC.."}, "HC.."),
        ({TeleinfoLabel.PTEC: "HP.."}, "HP.."),
        ({TeleinfoLabel.PTEC: "HN"}, "HN"),
        # Cas erreur : PTEC absent → None
        ({}, None),
        # Cas erreur : PTEC présent mais None
        ({TeleinfoLabel.PTEC: None}, None),
    ],
)
def test_get_tarif_period(cache_data, expected):
    result = get_tarif_period(cache_data)
    assert result == expected


@pytest.mark.parametrize(
    "cache_data, expected",
    [
        # Cas nominal : données complètes avec clés valides
        (
            {"HCHC": "123", "HCHP": "456", "OTHER": "999"},
            {"HCHC": 123, "HCHP": 456},
        ),
        # Cas : cache_data None → retourne None
        (
            None,
            None,
        ),
        # Cas : cache_data vide → retourne dict vide
        (
            {},
            {},
        ),
        # Cas : clés valides mais valeurs non convertibles → ValueError attendue
        # (on ne gère pas cette erreur dans la fonction, donc on le teste ici)
    ],
)
def test_get_indexes_in_teleinfo(cache_data, expected):
    if cache_data is not None and any(
        key in TELEINFO_INDEX_LABELS and not value.isdigit()
        for key, value in cache_data.items()
    ):
        # On attend une exception si conversion impossible
        with pytest.raises(ValueError):
            get_indexes_in_teleinfo(cache_data)
    else:
        result = get_indexes_in_teleinfo(cache_data)
        assert result == expected


SAMPLE_PERIODS = {**get_daily_index_structure(1), "07:00": "HC"}


@pytest.mark.parametrize(
    "initial_tarif_periods, now_minute_str, new_tarif_period, expected_tarif_periods",
    [
        # cas normal
        (SAMPLE_PERIODS, "07:01", "HC", {**SAMPLE_PERIODS, "07:01": "HC"}),
        # Tarif_periods None ou trop court → génération structure complète
        (None, "07:10", "HC", {**get_daily_index_structure(1), "07:10": "HC"}),
        ({}, "07:10", "HC", {**get_daily_index_structure(1), "07:10": "HC"}),
        # now_minute_str is None
        (SAMPLE_PERIODS, None, "HC", SAMPLE_PERIODS),
        # Cas décalage : 07:00 != 07:01 → correction de 07:00 à valeur 07:01
        (
            SAMPLE_PERIODS,
            "07:01",
            "HP",
            {**SAMPLE_PERIODS, "07:00": "HP", "07:01": "HP"},
        ),
        # cas décalage avec :00 = None
        (
            get_daily_index_structure(1),
            "07:01",
            "HP",
            {**get_daily_index_structure(1), "07:00": "HP", "07:01": "HP"},
        ),
    ],
)
def test_add_new_tarif_period(
    initial_tarif_periods, now_minute_str, new_tarif_period, expected_tarif_periods
):
    tarif_periods = deepcopy(initial_tarif_periods)
    result = add_new_tarif_period(tarif_periods, now_minute_str, new_tarif_period)
    assert result == expected_tarif_periods
    assert len(result) == 1441


class DailyIndexes:
    def __init__(self):
        self.values: dict[str, dict[str, int | None]] = {}


@pytest.mark.parametrize(
    "initial_values, new_data, minute, expected_values",
    [
        # Cas simple : le label existe déjà
        (
            {"HCHC": {"07:00": 1000}},  # initial
            {"HCHC": 1050},  # nouveau
            "07:01",
            {"HCHC": {"07:00": 1000, "07:01": 1050}},
        ),
        # Cas nouveau label → création du label avec structure complète
        (
            {},  # aucun label
            {"HCHP": 2000},  # nouveau label
            "08:30",
            {"HCHP": {**get_daily_index_structure(1), "08:30": 2000}},
        ),
        # Cas plusieurs labels
        (
            {"HCHC": {"08:00": 4000}},
            {"HCHC": 4050, "HCHP": 3100},
            "08:15",
            {
                "HCHC": {"08:00": 4000, "08:15": 4050},
                "HCHP": {**get_daily_index_structure(1), "08:15": 3100},
            },
        ),
    ],
)
def test_add_new_values(initial_values, new_data, minute, expected_values):
    today = DailyIndexes()
    today.values = {label: dict(val) for label, val in initial_values.items()}

    updated = add_new_values(today, new_data, minute)

    for label, expected_dict in expected_values.items():
        assert label in updated.values
        for time, expected_val in expected_dict.items():
            assert updated.values[label].get(time) == expected_val


@pytest.mark.parametrize(
    "today_indexes, new_data, minute",
    [
        (None, {"HCHC": 12345}, "07:00"),
        (DailyIndexes(), None, "07:00"),
        (DailyIndexes(), {"HCHC": 12345}, None),
    ],
)
def test_add_new_values_invalid_inputs(today_indexes, new_data, minute):
    result = add_new_values(today_indexes, new_data, minute)
    assert result == today_indexes


@pytest.mark.parametrize(
    "day, tarif_period, wh, expected",
    [
        # 50 Wh à 16.96 c€/kWh = 0.1696 €/kWh → 0.05 * 0.1696 = 0.00848 €
        (date(2025, 2, 1), "HC..", 50, 0.00848),
        # 100 Wh à 21.46 c€/kWh = 0.2146 €/kWh → 0.1 * 0.2146 = 0.02146 €
        (date(2025, 2, 1), "HP..", 100, 0.02146),
        # 1000 Wh à 0.2 c€/kWh = 0.002 €/kWh → 1 * 0.002 = 0.002 €
        (date(2024, 2, 2), "HC..", 1000, 0.002),
        # Tarif inconnu → prix = 0
        (date(2025, 2, 1), "UNKNOWN", 100, 0.0),
        # wh == 0 → None
        (date(2025, 2, 1), "HC..", 0, 0),
        # wh == None → None
        (date(2025, 2, 1), "HC..", None, None),
    ],
)
def test_compute_period_price(day, tarif_period, wh, expected):
    result = compute_period_price(day, tarif_period, wh)

    if expected is None:
        assert result is None
    elif expected == 0:
        assert result == 0
    else:
        assert round(result, 5) == round(expected, 5)


@pytest.mark.parametrize(
    "index_label, expected",
    [
        (TeleinfoLabel.BASE, TarifPeriods.TH),
        (TeleinfoLabel.HCHC, TarifPeriods.HC),
        (TeleinfoLabel.HCHP, TarifPeriods.HP),
        (TeleinfoLabel.EJPHN, TarifPeriods.HN),
        (TeleinfoLabel.EJPHPM, TarifPeriods.PM),
        (TeleinfoLabel.BBRHCJB, TarifPeriods.HCJB),
        (TeleinfoLabel.BBRHCJW, TarifPeriods.HCJW),
        (TeleinfoLabel.BBRHCJR, TarifPeriods.HCJR),
        (TeleinfoLabel.BBRHPJB, TarifPeriods.HPJB),
        (TeleinfoLabel.BBRHPJW, TarifPeriods.HPJW),
        (TeleinfoLabel.BBRHPJR, TarifPeriods.HPJR),
        ("UNKNOWN", None),  # test fallback case
    ],
)
def test_get_tarif_period_label_from_index_label(index_label, expected):
    assert get_tarif_period_label_from_index_label(index_label) == expected
