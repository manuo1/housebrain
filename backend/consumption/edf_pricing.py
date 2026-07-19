from datetime import date

from teleinfo.constants import TarifPeriods

pricing = {
    date(2026, 6, 26): {
        "kwh": {
            TarifPeriods.TH: 0,
            TarifPeriods.HC: 13.3692,
            TarifPeriods.HP: 17.2572,
            TarifPeriods.HN: 0,
            TarifPeriods.PM: 0,
            TarifPeriods.HCJB: 0,
            TarifPeriods.HPJB: 0,
            TarifPeriods.HCJW: 0,
            TarifPeriods.HPJW: 0,
            TarifPeriods.HCJR: 0,
            TarifPeriods.HPJR: 0,
        }
    },
    date(2025, 7, 10): {
        "kwh": {
            TarifPeriods.TH: 0,
            TarifPeriods.HC: 14.1854,
            TarifPeriods.HP: 17.8754,
            TarifPeriods.HN: 0,
            TarifPeriods.PM: 0,
            TarifPeriods.HCJB: 0,
            TarifPeriods.HPJB: 0,
            TarifPeriods.HCJW: 0,
            TarifPeriods.HPJW: 0,
            TarifPeriods.HCJR: 0,
            TarifPeriods.HPJR: 0,
        }
    },
    date(2025, 2, 1): {
        "kwh": {
            TarifPeriods.TH: 0,
            TarifPeriods.HC: 16.96,
            TarifPeriods.HP: 21.46,
            TarifPeriods.HN: 0,
            TarifPeriods.PM: 0,
            TarifPeriods.HCJB: 0,
            TarifPeriods.HPJB: 0,
            TarifPeriods.HCJW: 0,
            TarifPeriods.HPJW: 0,
            TarifPeriods.HCJR: 0,
            TarifPeriods.HPJR: 0,
        }
    },
    date(2024, 2, 1): {
        "kwh": {
            TarifPeriods.TH: 0,
            TarifPeriods.HC: 0,
            TarifPeriods.HP: 0,
            TarifPeriods.HN: 0,
            TarifPeriods.PM: 0,
            TarifPeriods.HCJB: 0,
            TarifPeriods.HPJB: 0,
            TarifPeriods.HCJW: 0,
            TarifPeriods.HPJW: 0,
            TarifPeriods.HCJR: 0,
            TarifPeriods.HPJR: 0,
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
