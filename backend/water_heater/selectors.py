from datetime import date

from water_heater.models import WaterHeaterDayPlan


def get_water_heaters_plans_data(day: date) -> list[dict]:
    return list(
        WaterHeaterDayPlan.objects.filter(date=day).values(
            "water_heater_id",
            "schedule_pattern__slots",
            "water_heater__requested_state",
        )
    )
