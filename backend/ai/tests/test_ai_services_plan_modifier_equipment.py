import json
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.plan_modifier import (
    _normalize_equipment_plan,
    _validate_equipment_plan,
    modify_equipment_plan,
)
from planning.models import SchedulePattern

# _parse_llm_response, _check_success and _infer_slot_type are shared with the
# heating flow and already covered in test_ai_services_plan_modifier.py.


# ------------------------------------------------------------------------------
# _normalize_equipment_plan
# ------------------------------------------------------------------------------


def test_normalize_equipment_plan_infers_type_on_every_slot_of_every_equipment():
    plan = {
        "equipments": [
            {
                "type": "water_heater",
                "id": 1,
                "slots": [{"start": "08:00", "end": "09:00", "value": "on"}],
            },
            {
                "type": "water_heater",
                "id": 2,
                "slots": [{"start": "08:00", "end": "09:00", "value": "off"}],
            },
        ]
    }

    result = _normalize_equipment_plan(plan)

    assert result["equipments"][0]["slots"][0]["type"] == "onoff"
    assert result["equipments"][1]["slots"][0]["type"] == "onoff"


def test_normalize_equipment_plan_handles_equipment_without_slots_key():
    plan = {"equipments": [{"type": "water_heater", "id": 1}]}
    assert _normalize_equipment_plan(plan) == {
        "equipments": [{"type": "water_heater", "id": 1, "slots": []}]
    }


def test_normalize_equipment_plan_handles_missing_equipments_key():
    assert _normalize_equipment_plan({}) == {}


# ------------------------------------------------------------------------------
# _validate_equipment_plan
# ------------------------------------------------------------------------------


@pytest.mark.parametrize("plan", [[], "not a dict", None, 42])
def test_validate_equipment_plan_rejects_non_dict(plan):
    with pytest.raises(DRFValidationError) as excinfo:
        _validate_equipment_plan(plan)

    assert "invalide" in str(excinfo.value.detail)


@pytest.mark.parametrize(
    "plan", [{}, {"equipments": "not a list"}, {"equipments": None}]
)
def test_validate_equipment_plan_rejects_missing_or_invalid_equipments(plan):
    with pytest.raises(DRFValidationError) as excinfo:
        _validate_equipment_plan(plan)

    assert "pas d'équipements" in str(excinfo.value.detail)


@pytest.mark.django_db
def test_validate_equipment_plan_accepts_valid_slots():
    plan = {
        "equipments": [
            {
                "type": "water_heater",
                "id": 1,
                "name": "Cuve",
                "slots": [
                    {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}
                ],
            }
        ]
    }

    _validate_equipment_plan(plan)  # must not raise

    assert SchedulePattern.objects.count() == 1


@pytest.mark.django_db
def test_validate_equipment_plan_rejects_invalid_slots_with_equipment_name_in_message():
    plan = {
        "equipments": [
            {
                "type": "water_heater",
                "id": 1,
                "name": "Cuve",
                # start after end -> invalid, SchedulePattern.clean() will reject it
                "slots": [
                    {"start": "09:00", "end": "07:00", "type": "onoff", "value": "on"}
                ],
            }
        ]
    }

    with pytest.raises(DRFValidationError) as excinfo:
        _validate_equipment_plan(plan)

    assert "Cuve" in str(excinfo.value.detail)


# ------------------------------------------------------------------------------
# modify_equipment_plan (full flow)
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_modify_equipment_plan_full_flow_returns_normalized_and_validated_plan():
    llm_response = json.dumps(
        {
            "success": True,
            "reason": "",
            "date": "2026-01-01",
            "equipments": [
                {
                    "type": "water_heater",
                    "id": 1,
                    "name": "Cuve",
                    "slots": [{"start": "07:00", "end": "09:00", "value": "on"}],
                }
            ],
        }
    )
    mock_client = MagicMock()
    mock_client.generate.return_value = llm_response

    with patch("ai.services.plan_modifier._get_llm_client", return_value=mock_client):
        result = modify_equipment_plan(
            instruction="allume le chauffe-eau de 7h à 9h",
            plan={"equipments": []},
        )

    assert "success" not in result
    assert "reason" not in result
    assert result["equipments"][0]["slots"][0]["type"] == "onoff"


@pytest.mark.django_db
def test_modify_equipment_plan_propagates_llm_reported_failure():
    llm_response = json.dumps({"success": False, "reason": "Équipement inconnu"})
    mock_client = MagicMock()
    mock_client.generate.return_value = llm_response

    with patch("ai.services.plan_modifier._get_llm_client", return_value=mock_client):
        with pytest.raises(DRFValidationError) as excinfo:
            modify_equipment_plan(
                instruction="allume la piscine", plan={"equipments": []}
            )

    assert str(excinfo.value.detail[0]) == "Équipement inconnu"
