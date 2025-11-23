from datetime import datetime

import pytest
from actuators.models import Radiator
from actuators.mutators.radiators import apply_load_shedding_to_radiators
from actuators.tests.factories import RadiatorFactory
from django.utils import timezone
from freezegun import freeze_time

DT1 = timezone.make_aware(datetime(2025, 10, 18, 8))
DT2 = timezone.make_aware(datetime(2025, 10, 18, 12))


@pytest.mark.django_db
@freeze_time(DT2)
def test_Apply_load_shedding_to_radiators():
    ID_TO_CHANGE = 1

    r1 = RadiatorFactory(
        id=ID_TO_CHANGE,
        requested_state=Radiator.RequestedState.ON,
        last_requested=DT1,
    )
    r2 = RadiatorFactory(
        id=2,
        requested_state=Radiator.RequestedState.ON,
        last_requested=DT1,
    )

    apply_load_shedding_to_radiators([ID_TO_CHANGE])

    r1.refresh_from_db(fields=["requested_state", "last_requested"])
    r2.refresh_from_db(fields=["requested_state", "last_requested"])

    # Radiateur qui avait l'id du radiateur à changer
    assert (
        r1.requested_state == Radiator.RequestedState.LOAD_SHED
        and r1.last_requested == DT2
    )
    # Ne devait pas changer
    assert r2.requested_state == Radiator.RequestedState.ON and r2.last_requested == DT1
