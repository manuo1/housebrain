from datetime import date
from teleinfo.constants import TarifPeriods

pricing = {
    date(2025, 2, 1): {
        "kwh": {
            TarifPeriods.TH: 20.16,
            TarifPeriods.HC: 16.96,
            TarifPeriods.HP: 21.46,
            TarifPeriods.HN: 0,
            TarifPeriods.PM: 0,
            TarifPeriods.HCJB: 12.88,
            TarifPeriods.HPJB: 15.52,
            TarifPeriods.HCJW: 14.47,
            TarifPeriods.HPJW: 17.92,
            TarifPeriods.HCJR: 15.18,
            TarifPeriods.HPJR: 65.86,
        }
    },
    date(2024, 2, 1): {
        "kwh": {
            TarifPeriods.TH: 0.1,
            TarifPeriods.HC: 0.2,
            TarifPeriods.HP: 0.3,
            TarifPeriods.HN: 0.4,
            TarifPeriods.PM: 0.5,
            TarifPeriods.HCJB: 0.6,
            TarifPeriods.HPJB: 0.7,
            TarifPeriods.HCJW: 0.8,
            TarifPeriods.HPJW: 0.9,
            TarifPeriods.HCJR: 1.0,
            TarifPeriods.HPJR: 1.1,
        }
    },
}


def get_kwh_price(date: date, tarif_period: str) -> float:
    start_date_list = sorted(pricing.keys(), reverse=True)
    if date < start_date_list[-1]:
        return 0
    for start_date in start_date_list:
        if date >= start_date:
            try:
                return pricing[start_date]["kwh"][tarif_period] / 100
            except KeyError:
                return 0
