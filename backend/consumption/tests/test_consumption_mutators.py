import pytest
from freezegun import freeze_time

from consumption.models import DailyIndexes
from consumption.mutators import save_teleinfo_data
from teleinfo.constants import TarifPeriods, TeleinfoLabel


def fake_cache_teleinfo_data():
    return {
        TeleinfoLabel.ISOUSC: "30",
        TeleinfoLabel.PTEC: TarifPeriods.HC,
        TeleinfoLabel.HCHC: "12345",
        TeleinfoLabel.HCHP: "6789",
    }


@pytest.mark.django_db
def test_save_teleinfo_data_does_nothing_if_cache_is_none(mocker):
    mocker.patch(
        "consumption.mutators.get_teleinfo_data_in_cache_if_up_to_date",
        return_value=None,
    )

    save_teleinfo_data()

    assert DailyIndexes.objects.count() == 0


@pytest.mark.django_db
@freeze_time("2025-06-01 08:15:00")  # 10:15 heure locale Europe/Paris (CEST, UTC+2 en juin)
def test_save_teleinfo_data_updates_current_day(mocker):
    mocker.patch(
        "consumption.mutators.get_teleinfo_data_in_cache_if_up_to_date",
        return_value=fake_cache_teleinfo_data(),
    )

    save_teleinfo_data()

    assert DailyIndexes.objects.count() == 1
    today_indexes = DailyIndexes.objects.get()
    assert today_indexes.date.isoformat() == "2025-06-01"
    assert today_indexes.subscribed_power == 6
    assert today_indexes.tarif_periods["10:15"] == TarifPeriods.HC
    assert today_indexes.values["HCHC"]["10:15"] == 12345
    assert today_indexes.values["HCHP"]["10:15"] == 6789


@pytest.mark.django_db
@freeze_time("2025-06-01 22:00:00")  # 00:00 heure locale Europe/Paris le 2025-06-02 (CEST, UTC+2 en juin)
def test_save_teleinfo_data_also_updates_previous_day_at_midnight(mocker):
    mocker.patch(
        "consumption.mutators.get_teleinfo_data_in_cache_if_up_to_date",
        return_value=fake_cache_teleinfo_data(),
    )

    save_teleinfo_data()

    assert DailyIndexes.objects.count() == 2

    today_indexes = DailyIndexes.objects.get(date="2025-06-02")
    assert today_indexes.tarif_periods["00:00"] == TarifPeriods.HC
    assert today_indexes.values["HCHC"]["00:00"] == 12345

    previous_day_indexes = DailyIndexes.objects.get(date="2025-06-01")
    assert previous_day_indexes.tarif_periods["24:00"] == TarifPeriods.HC
    assert previous_day_indexes.values["HCHC"]["24:00"] == 12345
    assert previous_day_indexes.subscribed_power == 6
