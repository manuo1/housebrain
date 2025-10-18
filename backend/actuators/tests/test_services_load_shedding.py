import pytest
from actuators.constants import POWER_SAFETY_MARGIN
from actuators.models import Radiator
from actuators.services.load_shedding import (
    manage_load_shedding,
    select_radiators_for_load_shedding,
)
from actuators.tests.factories import RadiatorFactory

RADIATORS_ON_1 = [
    {"id": 2, "power": 750, "importance": 3},
    {"id": 11, "power": 1250, "importance": 3},
    {"id": 4, "power": 750, "importance": 2},
    {"id": 5, "power": 1000, "importance": 2},
    {"id": 10, "power": 1500, "importance": 2},
    {"id": 13, "power": 1500, "importance": 2},
    {"id": 3, "power": 1500, "importance": 1},
    {"id": 8, "power": 1500, "importance": 1},
]


@pytest.mark.parametrize(
    "available_power, radiators_on, expected",
    [
        # 1500w restant + 750w de id=1 = 2250w, 2250w > POWER_SAFETY_MARGIN = 2000
        (1500, RADIATORS_ON_1, [2]),
        # 0w restant + 750w de id=1 + 1250w de id=11 = 2000w, 2000W = POWER_SAFETY_MARGIN = 2000
        (0, RADIATORS_ON_1, [2, 11]),
        # si la puissance consommée est supérieur à la puissance autorisée
        (-1500, RADIATORS_ON_1, [2, 11, 4, 5]),
        # PLus accès à la teleinfo -> éteint tous les radiateurs sauf importance 0 et 1
        (None, RADIATORS_ON_1, [2, 11, 4, 5, 10, 13]),
    ],
)
def test_select_radiators_for_load_shedding(available_power, radiators_on, expected):
    assert select_radiators_for_load_shedding(available_power, radiators_on) == expected


@pytest.mark.django_db
def test_manage_load_shedding():
    r1 = RadiatorFactory(power=750, importance=3, actual_state=Radiator.ActualState.ON)
    r2 = RadiatorFactory(power=1250, importance=3, actual_state=Radiator.ActualState.ON)
    r3 = RadiatorFactory(power=3000, importance=2, actual_state=Radiator.ActualState.ON)
    # ActualState.OFF -> ne serra pas sélectionné
    r8 = RadiatorFactory(power=100, importance=1, actual_state=Radiator.ActualState.OFF)
    # power == 0 -> ne serra pas sélectionné
    r9 = RadiatorFactory(power=0, importance=1, actual_state=Radiator.ActualState.ON)

    manage_load_shedding(POWER_SAFETY_MARGIN - 750 - 1250)

    radiators_with_load_shed = Radiator.objects.filter(
        requested_state=Radiator.RequestedState.LOAD_SHED
    )
    for radiator in [r3, r8, r9]:
        assert radiator not in radiators_with_load_shed
    for radiator in [r1, r2]:
        assert radiator in radiators_with_load_shed
