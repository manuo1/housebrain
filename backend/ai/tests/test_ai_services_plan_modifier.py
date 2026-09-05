import json
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.plan_modifier import (
    _check_success,
    _infer_slot_type,
    _normalize_plan,
    _parse_llm_response,
    _validate_plan,
    modify_heating_plan,
)
from ai.services.groq_client import GroqClient
from planning.models import SchedulePattern


# ------------------------------------------------------------------------------
# _parse_llm_response
# ------------------------------------------------------------------------------


def test_parse_llm_response_valid_json():
    raw = '{"success": true, "rooms": []}'
    assert _parse_llm_response(raw) == {"success": True, "rooms": []}


def test_parse_llm_response_strips_markdown_code_block():
    raw = '```json\n{"success": true, "rooms": []}\n```'
    assert _parse_llm_response(raw) == {"success": True, "rooms": []}


def test_parse_llm_response_invalid_json_raises():
    with pytest.raises(DRFValidationError) as excinfo:
        _parse_llm_response("this is not json")

    assert "format valide" in str(excinfo.value.detail)


# ------------------------------------------------------------------------------
# _check_success
# ------------------------------------------------------------------------------


def test_check_success_true_does_not_raise():
    _check_success({"success": True})


def test_check_success_false_raises_with_reason():
    with pytest.raises(DRFValidationError) as excinfo:
        _check_success({"success": False, "reason": "Pièce inconnue"})

    assert str(excinfo.value.detail[0]) == "Pièce inconnue"


def test_check_success_false_without_reason_uses_default_message():
    with pytest.raises(DRFValidationError) as excinfo:
        _check_success({"success": False})

    assert "n'a pas pu être appliquée" in str(excinfo.value.detail)


@pytest.mark.parametrize("parsed", [{}, {"success": None}, {"success": "yes"}])
def test_check_success_missing_or_invalid_field_raises_generic_message(parsed):
    with pytest.raises(DRFValidationError) as excinfo:
        _check_success(parsed)

    assert "format valide" in str(excinfo.value.detail)


# ------------------------------------------------------------------------------
# _infer_slot_type
# ------------------------------------------------------------------------------


def test_infer_slot_type_leaves_existing_type_untouched():
    slot = {"start": "08:00", "end": "09:00", "type": "onoff", "value": "on"}
    assert _infer_slot_type(dict(slot)) == slot


@pytest.mark.parametrize("value", ["on", "ON", "off", "OFF"])
def test_infer_slot_type_detects_onoff_case_insensitive(value):
    slot = {"start": "08:00", "end": "09:00", "value": value}
    result = _infer_slot_type(slot)
    assert result["type"] == "onoff"
    assert result["value"] == value


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (20, 20.0),
        (20.5, 20.5),
        ("20", 20.0),
        ("20.5", 20.5),
    ],
)
def test_infer_slot_type_detects_temp_and_casts_to_float(value, expected_value):
    slot = {"start": "08:00", "end": "09:00", "value": value}
    result = _infer_slot_type(slot)
    assert result["type"] == "temp"
    assert result["value"] == expected_value


def test_infer_slot_type_leaves_uncastable_value_for_validate_plan_to_catch():
    """A value that's neither on/off nor numeric is left as-is (invalid),
    the responsibility to reject it belongs to _validate_plan downstream."""
    slot = {"start": "08:00", "end": "09:00", "value": "not a number"}
    result = _infer_slot_type(slot)
    assert result["type"] == "temp"
    assert result["value"] == "not a number"


# ------------------------------------------------------------------------------
# _normalize_plan
# ------------------------------------------------------------------------------


def test_normalize_plan_infers_type_on_every_slot_of_every_room():
    plan = {
        "rooms": [
            {"room_id": 1, "slots": [{"start": "08:00", "end": "09:00", "value": "on"}]},
            {"room_id": 2, "slots": [{"start": "08:00", "end": "09:00", "value": 20}]},
        ]
    }

    result = _normalize_plan(plan)

    assert result["rooms"][0]["slots"][0]["type"] == "onoff"
    assert result["rooms"][1]["slots"][0]["type"] == "temp"


def test_normalize_plan_handles_room_without_slots_key():
    plan = {"rooms": [{"room_id": 1}]}
    assert _normalize_plan(plan) == {"rooms": [{"room_id": 1, "slots": []}]}


def test_normalize_plan_handles_missing_rooms_key():
    assert _normalize_plan({}) == {}


# ------------------------------------------------------------------------------
# _validate_plan
# ------------------------------------------------------------------------------


@pytest.mark.parametrize("plan", [[], "not a dict", None, 42])
def test_validate_plan_rejects_non_dict(plan):
    with pytest.raises(DRFValidationError) as excinfo:
        _validate_plan(plan)

    assert "invalide" in str(excinfo.value.detail)


@pytest.mark.parametrize("plan", [{}, {"rooms": "not a list"}, {"rooms": None}])
def test_validate_plan_rejects_missing_or_invalid_rooms(plan):
    with pytest.raises(DRFValidationError) as excinfo:
        _validate_plan(plan)

    assert "pas de pièces" in str(excinfo.value.detail)


@pytest.mark.django_db
def test_validate_plan_accepts_valid_slots():
    plan = {
        "rooms": [
            {
                "room_id": 1,
                "name": "Salon",
                "slots": [
                    {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0}
                ],
            }
        ]
    }

    _validate_plan(plan)  # must not raise

    assert SchedulePattern.objects.count() == 1


@pytest.mark.django_db
def test_validate_plan_rejects_invalid_slots_with_room_name_in_message():
    plan = {
        "rooms": [
            {
                "room_id": 1,
                "name": "Salon",
                # start after end -> invalid, SchedulePattern.clean() will reject it
                "slots": [
                    {"start": "09:00", "end": "07:00", "type": "temp", "value": 20.0}
                ],
            }
        ]
    }

    with pytest.raises(DRFValidationError) as excinfo:
        _validate_plan(plan)

    assert "Salon" in str(excinfo.value.detail)


# ------------------------------------------------------------------------------
# modify_heating_plan (full flow)
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_modify_heating_plan_full_flow_returns_normalized_and_validated_plan():
    llm_response = json.dumps(
        {
            "success": True,
            "reason": "",
            "date": "2026-01-01",
            "rooms": [
                {
                    "room_id": 1,
                    "name": "Salon",
                    "slots": [{"start": "07:00", "end": "09:00", "value": "on"}],
                }
            ],
        }
    )
    mock_client = MagicMock()
    mock_client.generate.return_value = llm_response

    with patch("ai.services.plan_modifier._get_llm_client", return_value=mock_client):
        result = modify_heating_plan(
            instruction="allume le salon de 7h à 9h",
            plan={"rooms": []},
        )

    assert "success" not in result
    assert "reason" not in result
    assert result["rooms"][0]["slots"][0]["type"] == "onoff"


@pytest.mark.django_db
def test_modify_heating_plan_propagates_llm_reported_failure():
    llm_response = json.dumps({"success": False, "reason": "Pièce inconnue"})
    mock_client = MagicMock()
    mock_client.generate.return_value = llm_response

    with patch("ai.services.plan_modifier._get_llm_client", return_value=mock_client):
        with pytest.raises(DRFValidationError) as excinfo:
            modify_heating_plan(instruction="allume la cave", plan={"rooms": []})

    assert str(excinfo.value.detail[0]) == "Pièce inconnue"


def test_get_llm_client_returns_groq_client():
    """Default provider is Groq (see the comment on how to swap providers)."""
    from ai.services.plan_modifier import _get_llm_client

    with patch("ai.services.groq_client.settings.GROQ_API_KEY", "fake-key"):
        assert isinstance(_get_llm_client(), GroqClient)
