import pytest
from datetime import date
from consumption.edf_pricing import get_kwh_price
from teleinfo.constants import TarifPeriods


@pytest.mark.parametrize(
    "target_date, period, expected_price",
    [
        # Cas standard, tarif applicable à la date de 2025-06-01 (doit prendre 2025-02-01)
        (date(2025, 6, 1), TarifPeriods.HP, 21.46 / 100),
        (date(2025, 6, 1), TarifPeriods.HCJR, 15.18 / 100),
        # Cas où la date est avant 2025-02-01 mais après 2024-02-01
        (date(2024, 6, 1), TarifPeriods.HC, 0.2 / 100),
        (date(2024, 3, 1), TarifPeriods.HPJR, 1.1 / 100),
        # Cas exact sur les bornes
        (date(2025, 2, 1), TarifPeriods.HC, 16.96 / 100),
        (date(2024, 2, 1), TarifPeriods.HN, 0.4 / 100),
        # Cas avant toute période connue
        (date(2023, 12, 31), TarifPeriods.HC, 0 / 100),  # pas de grille applicable
        # Cas où la période tarifaire n’existe pas dans la grille
        (date(2025, 6, 1), "UNKNOWN_PERIOD", 0 / 100),
    ],
)
def test_get_kwh_price(target_date, period, expected_price):
    result = get_kwh_price(target_date, period)
    assert result == expected_price
