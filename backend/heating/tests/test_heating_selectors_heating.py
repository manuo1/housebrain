from datetime import date, timedelta

import pytest
from actuators.tests.factories import RadiatorFactory
from heating.selectors.heating import get_rooms_heating_plans_data
from heating.tests.factories import (
    HeatingPatternFactory,
    HeatingPatternOnOffFactory,
    RoomHeatingDayPlanFactory,
)
from rooms.models import Room
from rooms.tests.factories import RoomFactory
from sensors.tests.factories import TemperatureSensorFactory


@pytest.mark.django_db
def test_get_rooms_heating_plans_data_select():
    DATE = date(2025, 11, 27)

    RoomHeatingDayPlanFactory(
        date=DATE,
        heating_pattern=HeatingPatternFactory(),
        room=RoomFactory(
            id=1,
            radiator=RadiatorFactory(),
            temperature_sensor=TemperatureSensorFactory(mac_address="temp_mac"),
            heating_control_mode=Room.HeatingControlMode.THERMOSTAT,
            temperature_setpoint=12.0,
            requested_heating_state=Room.RequestedHeatingState.ON,
        ),
    )
    RoomHeatingDayPlanFactory(
        date=DATE,
        heating_pattern=HeatingPatternOnOffFactory(),
        room=RoomFactory(
            id=2,
            radiator=RadiatorFactory(),
            temperature_sensor=None,
            heating_control_mode=Room.HeatingControlMode.ONOFF,
            temperature_setpoint=None,
            requested_heating_state=Room.RequestedHeatingState.OFF,
        ),
    )
    # invalid : date
    RoomHeatingDayPlanFactory(
        date=DATE + timedelta(days=1),
        heating_pattern=HeatingPatternFactory(
            slots=[{"start": "07:00", "end": "09:00", "type": "temp", "value": 1.0}]
        ),
        room=RoomFactory(id=3),
    )
    # invalid : no radiator
    RoomHeatingDayPlanFactory(
        date=DATE,
        heating_pattern=HeatingPatternFactory(
            slots=[{"start": "07:00", "end": "09:00", "type": "temp", "value": 2.0}]
        ),
        room=RoomFactory(id=5, radiator=None),
    )

    assert get_rooms_heating_plans_data(DATE) == [
        {
            "room_id": 1,
            "heating_pattern__slots": [
                {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
                {"start": "18:00", "end": "22:00", "type": "temp", "value": 21.0},
            ],
            "room__temperature_sensor__mac_address": "temp_mac",
            "room__heating_control_mode": "thermostat",
            "room__temperature_setpoint": 12.0,
            "room__requested_heating_state": "on",
        },
        {
            "room_id": 2,
            "heating_pattern__slots": [
                {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
                {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"},
            ],
            "room__temperature_sensor__mac_address": None,
            "room__heating_control_mode": "on_off",
            "room__temperature_setpoint": None,
            "room__requested_heating_state": "off",
        },
    ]
