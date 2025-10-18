from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from freezegun import freeze_time
from mock_data.teleinfo import MOCKED_TELEINFO_DATA
from teleinfo.utils.cache_teleinfo_data import (
    get_teleinfo_data_in_cache,
    get_teleinfo_data_in_cache_if_up_to_date,
    set_teleinfo_data_in_cache,
)


@pytest.fixture
def mock_dev_environment(monkeypatch):
    monkeypatch.setattr(
        "teleinfo.utils.cache_teleinfo_data.environment_is_development", lambda: True
    )


@pytest.fixture
def mock_prod_environment(monkeypatch):
    monkeypatch.setattr(
        "teleinfo.utils.cache_teleinfo_data.environment_is_development", lambda: False
    )


NOW_ISOFORMAT_DT = timezone.now().isoformat()
TEN_SECONDS_BEFORE_ISOFORMAT_DT = (timezone.now() - timedelta(seconds=10)).isoformat()


@freeze_time(NOW_ISOFORMAT_DT)
def test_get_teleinfo_data_in_cache_dev_mode(mock_dev_environment):
    result = get_teleinfo_data_in_cache()
    assert result == MOCKED_TELEINFO_DATA
    assert result["last_read"] != NOW_ISOFORMAT_DT


@freeze_time(NOW_ISOFORMAT_DT)
def test_get_teleinfo_data_in_cache_if_up_to_date_dev_mode(mock_dev_environment):
    result = get_teleinfo_data_in_cache_if_up_to_date()
    assert result == MOCKED_TELEINFO_DATA
    assert result["last_read"] == NOW_ISOFORMAT_DT


@freeze_time(NOW_ISOFORMAT_DT)
def test_get_teleinfo_data_in_cache_prod_mode_cache_empty(mock_prod_environment):
    result = get_teleinfo_data_in_cache()
    assert result == {"last_read": None}


@freeze_time(NOW_ISOFORMAT_DT)
def test_get_teleinfo_data_in_cache_if_up_to_date_prod_mode_cache_empty(
    mock_prod_environment,
):
    result = get_teleinfo_data_in_cache_if_up_to_date()
    assert result is None


UP_TO_DATE_CACHE_DATA = {"some": "data", "last_read": NOW_ISOFORMAT_DT}
OUTDATED_CACHE_DATA = {"some": "data", "last_read": TEN_SECONDS_BEFORE_ISOFORMAT_DT}


@pytest.mark.parametrize("cache_data", (UP_TO_DATE_CACHE_DATA, OUTDATED_CACHE_DATA))
@freeze_time(NOW_ISOFORMAT_DT)
def test_get_teleinfo_data_in_cache_prod_mode_cache_not_empty(
    mock_prod_environment, cache_data
):
    cache.set("teleinfo_data", cache_data, timeout=None)
    result = get_teleinfo_data_in_cache()
    assert result == cache_data


@pytest.mark.parametrize(
    "cache_data, expected",
    [
        (UP_TO_DATE_CACHE_DATA, UP_TO_DATE_CACHE_DATA),
        (OUTDATED_CACHE_DATA, None),
    ],
    ids=["up_to_date", "outdated"],
)
@freeze_time(NOW_ISOFORMAT_DT)
def test_get_teleinfo_data_in_cache_if_up_to_date_prod_mode_cache_not_empty(
    mock_prod_environment, cache_data, expected
):
    cache.set("teleinfo_data", cache_data, timeout=None)
    result = get_teleinfo_data_in_cache_if_up_to_date()
    assert result == expected


def test_set_teleinfo_data_in_cache():
    cache.set("teleinfo_data", {}, timeout=None)
    set_teleinfo_data_in_cache(UP_TO_DATE_CACHE_DATA)
    assert cache.get("teleinfo_data") == UP_TO_DATE_CACHE_DATA
