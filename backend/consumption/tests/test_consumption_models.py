from datetime import date

import pytest

from consumption.models import DailyIndexes


@pytest.mark.django_db
def test_daily_indexes_str():
    daily_indexes = DailyIndexes.objects.create(date=date(2025, 6, 1))

    assert str(daily_indexes) == "Indexes du 2025-06-01"
