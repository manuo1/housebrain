from datetime import date, timedelta

import pytest

from consumption.constants import TarifPeriodType
from consumption.models import DailyIndexes
from consumption.utils import (
    fill_missing_tarif_periods,
    get_hc_hp_ref_day,
    get_tarif_period_type,
    get_tempo_color,
    get_tempo_ref_day,
)
from teleinfo.constants import TarifPeriods


def make_tarif_periods(**overrides: str | None) -> dict[str, str | None]:
    """Builds a minimal 3-slot tarif_periods dict, all None unless overridden."""
    base = {"00:00": None, "12:00": None, "24:00": None}
    base.update(overrides)
    return base


# --- get_tarif_period_type ---


def test_get_tarif_period_type_th():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.TH})
    assert get_tarif_period_type(tarif_periods) == TarifPeriodType.TH


def test_get_tarif_period_type_hc_hp():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HP})
    assert get_tarif_period_type(tarif_periods) == TarifPeriodType.HC_HP


def test_get_tarif_period_type_ejp():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.PM})
    assert get_tarif_period_type(tarif_periods) == TarifPeriodType.EJP


def test_get_tarif_period_type_tempo():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HPJR})
    assert get_tarif_period_type(tarif_periods) == TarifPeriodType.TEMPO


def test_get_tarif_period_type_none_when_empty():
    assert get_tarif_period_type(make_tarif_periods()) is None


# --- get_tempo_color ---


def test_get_tempo_color_detects_red():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HPJR})
    assert get_tempo_color(tarif_periods) == "R"


def test_get_tempo_color_none_when_not_tempo():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HC})
    assert get_tempo_color(tarif_periods) is None


# --- get_hc_hp_ref_day ---


@pytest.mark.django_db
def test_get_hc_hp_ref_day_finds_most_recent_complete_day():
    older_complete = {"00:00": TarifPeriods.HC, "12:00": TarifPeriods.HP}
    newer_complete = {"00:00": TarifPeriods.HP, "12:00": TarifPeriods.HC}
    DailyIndexes.objects.create(date=date(2025, 5, 29), tarif_periods=older_complete)
    DailyIndexes.objects.create(date=date(2025, 5, 31), tarif_periods=newer_complete)

    result = get_hc_hp_ref_day(date(2025, 6, 1))

    assert result == newer_complete


@pytest.mark.django_db
def test_get_hc_hp_ref_day_skips_incomplete_day():
    incomplete = {"00:00": TarifPeriods.HC, "12:00": None}
    complete = {"00:00": TarifPeriods.HP, "12:00": TarifPeriods.HC}
    DailyIndexes.objects.create(date=date(2025, 5, 31), tarif_periods=incomplete)
    DailyIndexes.objects.create(date=date(2025, 5, 30), tarif_periods=complete)

    result = get_hc_hp_ref_day(date(2025, 6, 1))

    assert result == complete


@pytest.mark.django_db
def test_get_hc_hp_ref_day_returns_none_when_no_candidate():
    assert get_hc_hp_ref_day(date(2025, 6, 1)) is None


@pytest.mark.django_db
def test_get_hc_hp_ref_day_ignores_day_outside_search_window():
    too_old = {"00:00": TarifPeriods.HC, "12:00": TarifPeriods.HP}
    DailyIndexes.objects.create(
        date=date(2025, 6, 1) - timedelta(days=10), tarif_periods=too_old
    )

    assert get_hc_hp_ref_day(date(2025, 6, 1)) is None


# --- get_tempo_ref_day ---


@pytest.mark.django_db
def test_get_tempo_ref_day_filters_by_color():
    red_day = {"00:00": TarifPeriods.HCJR, "12:00": TarifPeriods.HPJR}
    blue_day = {"00:00": TarifPeriods.HCJB, "12:00": TarifPeriods.HPJB}
    DailyIndexes.objects.create(date=date(2025, 5, 30), tarif_periods=blue_day)
    DailyIndexes.objects.create(date=date(2025, 5, 31), tarif_periods=red_day)

    result = get_tempo_ref_day(date(2025, 6, 1), "R")

    assert result == red_day


@pytest.mark.django_db
def test_get_tempo_ref_day_returns_none_when_color_is_none():
    assert get_tempo_ref_day(date(2025, 6, 1), None) is None


# --- fill_missing_tarif_periods ---


def test_fill_missing_tarif_periods_current_day_leaves_gaps():
    today = date.today()
    tarif_periods = make_tarif_periods(**{"00:00": TarifPeriods.HC})

    result = fill_missing_tarif_periods(tarif_periods, today)

    assert result == tarif_periods


def test_fill_missing_tarif_periods_th_fills_everything():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.TH})

    result = fill_missing_tarif_periods(tarif_periods, date(2025, 6, 1))

    assert all(value == TarifPeriods.TH for value in result.values())


def test_fill_missing_tarif_periods_ejp_leaves_gaps():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.PM})

    result = fill_missing_tarif_periods(tarif_periods, date(2025, 6, 1))

    assert result == tarif_periods


def test_fill_missing_tarif_periods_undetermined_leaves_gaps():
    tarif_periods = make_tarif_periods()

    result = fill_missing_tarif_periods(tarif_periods, date(2025, 6, 1))

    assert result == tarif_periods


@pytest.mark.django_db
def test_fill_missing_tarif_periods_hc_hp_reuses_ref_day():
    ref_day = {
        "00:00": TarifPeriods.HP,
        "12:00": TarifPeriods.HC,
        "24:00": TarifPeriods.HP,
    }
    DailyIndexes.objects.create(date=date(2025, 5, 31), tarif_periods=ref_day)
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HC})

    result = fill_missing_tarif_periods(tarif_periods, date(2025, 6, 1))

    assert result == ref_day


@pytest.mark.django_db
def test_fill_missing_tarif_periods_hc_hp_leaves_gaps_when_no_ref_day():
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HC})

    result = fill_missing_tarif_periods(tarif_periods, date(2025, 6, 1))

    assert result == tarif_periods


@pytest.mark.django_db
def test_fill_missing_tarif_periods_complete_day_skips_ref_day_lookup():
    # A reference day exists in DB and would be returned if the lookup ran;
    # since the target day is already complete, it must not run, and the
    # original data must be returned unchanged.
    ref_day = {
        "00:00": TarifPeriods.HP,
        "12:00": TarifPeriods.HC,
        "24:00": TarifPeriods.HP,
    }
    DailyIndexes.objects.create(date=date(2025, 5, 31), tarif_periods=ref_day)
    complete_tarif_periods = {
        "00:00": TarifPeriods.HC,
        "12:00": TarifPeriods.HP,
        "24:00": TarifPeriods.HC,
    }

    result = fill_missing_tarif_periods(complete_tarif_periods, date(2025, 6, 1))

    assert result == complete_tarif_periods


@pytest.mark.django_db
def test_fill_missing_tarif_periods_tempo_reuses_same_color_ref_day():
    red_ref_day = {
        "00:00": TarifPeriods.HCJR,
        "12:00": TarifPeriods.HPJR,
        "24:00": TarifPeriods.HCJR,
    }
    blue_ref_day = {
        "00:00": TarifPeriods.HCJB,
        "12:00": TarifPeriods.HPJB,
        "24:00": TarifPeriods.HCJB,
    }
    DailyIndexes.objects.create(date=date(2025, 5, 30), tarif_periods=blue_ref_day)
    DailyIndexes.objects.create(date=date(2025, 5, 31), tarif_periods=red_ref_day)
    tarif_periods = make_tarif_periods(**{"12:00": TarifPeriods.HPJR})

    result = fill_missing_tarif_periods(tarif_periods, date(2025, 6, 1))

    assert result == red_ref_day
