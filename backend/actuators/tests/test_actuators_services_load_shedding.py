import pytest

from actuators.models import Radiator
from actuators.services.load_shedding import manage_load_shedding
from actuators.tests.factories import RadiatorFactory
from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory


@pytest.mark.django_db
def test_manage_load_shedding():
    r1 = RadiatorFactory(power=750, importance=3, actual_state=Radiator.ActualState.ON)
    r2 = RadiatorFactory(power=1250, importance=3, actual_state=Radiator.ActualState.ON)
    r3 = RadiatorFactory(power=3000, importance=2, actual_state=Radiator.ActualState.ON)
    # ActualState.OFF -> ne serra pas sélectionné
    r8 = RadiatorFactory(power=100, importance=1, actual_state=Radiator.ActualState.OFF)
    # power == 0 -> ne serra pas sélectionné
    r9 = RadiatorFactory(power=0, importance=1, actual_state=Radiator.ActualState.ON)

    manage_load_shedding(-750 - 1250)

    radiators_with_load_shed = Radiator.objects.filter(
        requested_state=Radiator.RequestedState.LOAD_SHED
    )
    for radiator in [r3, r8, r9]:
        assert radiator not in radiators_with_load_shed
    for radiator in [r1, r2]:
        assert radiator in radiators_with_load_shed


@pytest.mark.django_db
def test_manage_load_shedding_does_not_shed_water_heater_when_radiators_are_enough(
    mocker,
):
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=True)
    r1 = RadiatorFactory(power=2000, importance=3, actual_state=Radiator.ActualState.ON)
    water_heater = WaterHeaterFactory(
        power=2000,
        requested_state=WaterHeater.RequestedState.ON,
        actual_state=WaterHeater.ActualState.ON,
    )

    manage_load_shedding(-2000)

    r1.refresh_from_db()
    water_heater.refresh_from_db()
    assert r1.requested_state == Radiator.RequestedState.LOAD_SHED
    # water heater kept on: radiators alone covered the deficit
    assert water_heater.requested_state == WaterHeater.RequestedState.ON


@pytest.mark.django_db
def test_manage_load_shedding_sheds_water_heater_when_radiators_are_not_enough(
    mocker,
):
    mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=False)
    r1 = RadiatorFactory(power=1000, importance=3, actual_state=Radiator.ActualState.ON)
    water_heater = WaterHeaterFactory(
        power=2000, actual_state=WaterHeater.ActualState.ON
    )

    # -3000W deficit, radiator only recovers 1000W: 2000W still short,
    # exactly the water heater's power
    manage_load_shedding(-3000)

    r1.refresh_from_db()
    water_heater.refresh_from_db()
    assert r1.requested_state == Radiator.RequestedState.LOAD_SHED
    assert water_heater.requested_state == WaterHeater.RequestedState.LOAD_SHED
