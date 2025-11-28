from datetime import date

from heating.models import RoomHeatingDayPlan


def get_rooms_heating_plans_data(date: date) -> list[dict]:
    return list(
        RoomHeatingDayPlan.objects.filter(
            date=date,
            room__radiator__isnull=False,
        ).values(
            "room_id",
            "heating_pattern__slots",
            "room__temperature_sensor__mac_address",
            "room__heating_control_mode",
            "room__temperature_setpoint",
            "room__requested_heating_state",
        )
    )
