import pytest
from actuators.models import Radiator
from actuators.selectors.radiators import (
    get_radiators_data_for_hardware_synchronization,
    get_radiators_data_for_load_shedding,
    get_radiators_data_for_on_off_heating_control,
)
from actuators.tests.factories import RadiatorFactory


@pytest.mark.django_db
def test_get_radiators_data_for_hardware_synchronization():
    RadiatorFactory(
        id=1,
        control_pin=1,
        requested_state=Radiator.RequestedState.ON,
        actual_state=Radiator.ActualState.ON,
        error="pas d'erreur",
        importance=Radiator.Importance.LOW,
    )
    RadiatorFactory(
        id=2,
        control_pin=2,
        requested_state=Radiator.RequestedState.OFF,
        actual_state=Radiator.ActualState.ON,
        error="pas d'erreur",
        importance=Radiator.Importance.LOW,
    )
    result = get_radiators_data_for_hardware_synchronization()
    assert result == [
        {
            "id": 1,
            "control_pin": 1,
            "requested_state": "ON",
            "actual_state": "ON",
            "error": "pas d'erreur",
        },
        {
            "id": 2,
            "control_pin": 2,
            "requested_state": "OFF",
            "actual_state": "ON",
            "error": "pas d'erreur",
        },
    ]


@pytest.mark.django_db
def test_get_radiators_data_for_hardware_synchronization_no_radiator():
    result = get_radiators_data_for_hardware_synchronization()
    assert result == []


@pytest.mark.django_db
def test_get_radiators_data_for_load_shedding_select():
    # power > 0 et ActualState.ON -> sera sélectionné
    RadiatorFactory(power=100, importance=1, actual_state=Radiator.ActualState.ON)
    # ActualState.OFF -> ne serra pas sélectionné
    RadiatorFactory(power=100, importance=1, actual_state=Radiator.ActualState.OFF)
    # power == 0 -> ne serra pas sélectionné
    RadiatorFactory(power=0, importance=1, actual_state=Radiator.ActualState.ON)
    result = get_radiators_data_for_load_shedding()
    assert result == [{"id": 1, "importance": 1, "power": 100}]


@pytest.mark.django_db
def test_get_radiators_data_for_load_shedding_no_radiator():
    result = get_radiators_data_for_load_shedding()
    assert result == []


@pytest.mark.django_db
def test_get_radiators_data_for_load_shedding_sort():
    """
    Importance:
        CRITICAL = 0
        HIGH = 1
        MEDIUM = 2
        LOW = 3
    """

    RadiatorFactory(power=100, importance=1, actual_state=Radiator.ActualState.ON)
    RadiatorFactory(power=100, importance=2, actual_state=Radiator.ActualState.ON)
    RadiatorFactory(power=200, importance=2, actual_state=Radiator.ActualState.ON)
    RadiatorFactory(power=100, importance=3, actual_state=Radiator.ActualState.ON)
    result = get_radiators_data_for_load_shedding()
    print(result)
    assert result == [
        # moins important en premier
        {"id": 4, "power": 100, "importance": 3},
        # Même importance donc plus forte puissance en premier
        {"id": 3, "power": 200, "importance": 2},
        {"id": 2, "power": 100, "importance": 2},
        # plus important donc en dernier
        {"id": 1, "power": 100, "importance": 1},
    ]


@pytest.mark.django_db
def test_get_radiators_data_for_on_off_heating_control():
    RadiatorFactory(
        id=1,
        requested_state=Radiator.RequestedState.ON,
        power=10,
        importance=Radiator.Importance.HIGH,
    )
    RadiatorFactory(
        id=2,
        requested_state=Radiator.RequestedState.OFF,
        power=10,
        importance=Radiator.Importance.HIGH,
    )
    RadiatorFactory(
        id=3,
        requested_state=Radiator.RequestedState.LOAD_SHED,
        power=10,
        importance=Radiator.Importance.HIGH,
    )
    RadiatorFactory(
        id=4,
        requested_state=Radiator.RequestedState.ON,
        power=10,
        importance=Radiator.Importance.HIGH,
    )
    RadiatorFactory(
        id=5,
        requested_state=Radiator.RequestedState.OFF,
        power=10,
        importance=Radiator.Importance.HIGH,
    )

    id_list = [1, 2, 3, 6]  # 6 n'existe pas dans la bdd

    result = get_radiators_data_for_on_off_heating_control(id_list)
    assert result == [
        {
            "id": 1,
            "requested_state": Radiator.RequestedState.ON,
            "power": 10,
            "importance": Radiator.Importance.HIGH,
        },
        {
            "id": 2,
            "requested_state": Radiator.RequestedState.OFF,
            "power": 10,
            "importance": Radiator.Importance.HIGH,
        },
        {
            "id": 3,
            "requested_state": Radiator.RequestedState.LOAD_SHED,
            "power": 10,
            "importance": Radiator.Importance.HIGH,
        },
    ]
