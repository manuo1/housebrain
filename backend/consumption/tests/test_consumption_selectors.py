from datetime import date

import pytest

from consumption.models import DailyIndexes
from consumption.selectors import get_daily_indexes


@pytest.mark.django_db
def test_get_daily_indexes_returns_only_dates_in_range():
    DailyIndexes.objects.create(date=date(2025, 5, 31))
    in_range_1 = DailyIndexes.objects.create(date=date(2025, 6, 1))
    in_range_2 = DailyIndexes.objects.create(date=date(2025, 6, 2))
    DailyIndexes.objects.create(date=date(2025, 6, 3))

    result = get_daily_indexes(date(2025, 6, 1), date(2025, 6, 3))

    assert result == [in_range_1, in_range_2]


@pytest.mark.django_db
def test_get_daily_indexes_returns_empty_list_when_nothing_matches():
    DailyIndexes.objects.create(date=date(2025, 6, 1))

    result = get_daily_indexes(date(2025, 7, 1), date(2025, 7, 2))

    assert result == []
