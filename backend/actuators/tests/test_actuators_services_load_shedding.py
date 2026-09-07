import pytest

from actuators.models import Radiator
from actuators.services.load_shedding import manage_load_shedding
from actuators.tests.factories import RadiatorFactory


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
