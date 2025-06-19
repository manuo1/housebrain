import pytest
from copy import deepcopy
from datetime import datetime
from consumption.constants import ALLOWED_CONSUMPTION_STEPS
from teleinfo.constants import TarifPeriods, TeleinfoLabel
from consumption.utils import (
    compute_indexes_missing_values,
    compute_totals,
    compute_watt_hours,
    downsample_indexes,
    fill_missing_values,
    find_all_missing_value_zones,
    generate_daily_index_structure,
    get_human_readable_tarif_period,
    get_index_label,
    get_wh_of_index_label,
    interpolate_missing_values,
    is_interpolated,
)


@pytest.mark.parametrize("step", ALLOWED_CONSUMPTION_STEPS)
def test_generate_daily_index_structure_valid_steps(step):
    result = generate_daily_index_structure(step)

    # Check that result is a dict
    assert isinstance(result, dict)

    # Check the expected number of time keys + "24:00"
    expected_keys = (24 * 60) // step + 1
    assert len(result) == expected_keys

    # Check that all keys except the last are spaced by `step` minutes
    time_keys = list(result.keys())
    for i in range(len(time_keys) - 2):  # exclude last which is "24:00"
        t1 = datetime.strptime(time_keys[i], "%H:%M")
        t2 = datetime.strptime(time_keys[i + 1], "%H:%M")
        delta = (t2 - t1).total_seconds() / 60
        assert delta == step

    assert time_keys[-1] == "24:00"
    assert result["24:00"] is None


def test_generate_daily_index_structure_invalid_type():
    with pytest.raises(TypeError):
        generate_daily_index_structure("30")


def test_generate_daily_index_structure_invalid_step():
    with pytest.raises(ValueError):
        generate_daily_index_structure(15)


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


import pytest


@pytest.mark.parametrize(
    "values, expected",
    [
        # Normal case
        (
            {
                "hp": {"00:00": 1000, "12:00": 1500, "24:00": 1600},
                "hc": {"00:00": 2000, "24:00": 2200},
            },
            {"hp": 600, "hc": 200},
        ),
        # None values at the start or end
        (
            {
                "hp": {"00:00": None, "06:00": 1200, "24:00": 1500},
                "hc": {"00:00": 1200, "06:00": 1500, "24:00": None},
            },
            {"hp": 300, "hc": 300},
        ),
        # None values at the start and end
        (
            {
                "hp": {"00:00": None, "06:00": 1200, "12:00": 1500, "24:00": None},
            },
            {"hp": 300},
        ),
        # Case where all values are None
        (
            {
                "hp": {"00:00": None, "06:00": None},
            },
            {"hp": None},
        ),
        # Index don't change
        (
            {
                "hp": {},
                "hc": {"00:00": 1234, "24:00": 1234},
            },
            {"hp": None, "hc": 0},
        ),
        # Not enough data
        (
            {
                "hc": {"00:00": 1234, "06:00": None, "24:00": None},
            },
            {"hc": None},
        ),
        # Empty input
        (
            {},
            {},
        ),
    ],
)
def test_compute_totals(values, expected):
    result = compute_totals(values)
    # only the wh for now, euro isn't implemented yet
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


import pytest


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
