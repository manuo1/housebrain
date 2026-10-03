import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.duplication_interpreter import (
    _validate_equipment_llm_shape,
    interpret_equipment_duplication_instruction,
)

# _parse_llm_response and VALID_STATUSES are shared with the heating flow.

TODAY = date(2026, 8, 15)
EQUIPMENTS = [{"key": "water_heater:1", "name": "Cumulus"}]
CONVERSATION = [{"role": "user", "content": "copie ce jour sur tous les mercredis"}]

READY = {
    "status": "ready",
    "message": "",
    "equipment_keys": ["water_heater:1"],
    "weekdays": [2],
    "start": "2026-08-16",
    "end": "2026-08-30",
}


# ------------------------------------------------------------------------------
# _validate_equipment_llm_shape
# ------------------------------------------------------------------------------


def test_validate_shape_accepts_ready():
    _validate_equipment_llm_shape(READY)  # must not raise


@pytest.mark.parametrize("status", ["clarify", "invalid"])
def test_validate_shape_accepts_non_ready_without_fields(status):
    _validate_equipment_llm_shape({"status": status, "message": "Précisez la date."})


@pytest.mark.parametrize("parsed", [[], "text", None, 42])
def test_validate_shape_rejects_non_dict(parsed):
    with pytest.raises(DRFValidationError):
        _validate_equipment_llm_shape(parsed)


@pytest.mark.parametrize(
    "parsed",
    [
        {"message": ""},  # status missing
        {"status": "unknown", "message": ""},
        {"status": "ready"},  # message missing
        {"status": "ready", "message": None},
    ],
)
def test_validate_shape_rejects_missing_or_unknown_status_and_message(parsed):
    with pytest.raises(DRFValidationError):
        _validate_equipment_llm_shape(parsed)


@pytest.mark.parametrize(
    "overrides",
    [
        {"equipment_keys": "water_heater:1"},  # not a list
        {"equipment_keys": [1]},  # not strings
        {"weekdays": None},
        {"start": None},
        {"end": 20260830},
    ],
)
def test_validate_shape_rejects_malformed_ready_fields(overrides):
    with pytest.raises(DRFValidationError):
        _validate_equipment_llm_shape({**READY, **overrides})


def test_validate_shape_rejects_ready_with_missing_field():
    parsed = {k: v for k, v in READY.items() if k != "equipment_keys"}

    with pytest.raises(DRFValidationError):
        _validate_equipment_llm_shape(parsed)


# ------------------------------------------------------------------------------
# interpret_equipment_duplication_instruction (full flow)
# ------------------------------------------------------------------------------


def _mock_client(response: dict) -> MagicMock:
    client = MagicMock()
    client.generate.return_value = json.dumps(response)
    return client


def test_interpret_returns_parsed_ready_response():
    client = _mock_client(READY)

    with patch(
        "ai.services.duplication_interpreter._get_llm_client", return_value=client
    ):
        result = interpret_equipment_duplication_instruction(
            CONVERSATION, TODAY, EQUIPMENTS
        )

    assert result == READY


def test_interpret_returns_clarify_response():
    response = {"status": "clarify", "message": "Jusqu'à quelle date ?"}
    client = _mock_client(response)

    with patch(
        "ai.services.duplication_interpreter._get_llm_client", return_value=client
    ):
        result = interpret_equipment_duplication_instruction(
            CONVERSATION, TODAY, EQUIPMENTS
        )

    assert result["status"] == "clarify"
    assert result["message"] == "Jusqu'à quelle date ?"


def test_interpret_sends_equipments_and_conversation_to_the_llm():
    client = _mock_client(READY)

    with patch(
        "ai.services.duplication_interpreter._get_llm_client", return_value=client
    ):
        interpret_equipment_duplication_instruction(CONVERSATION, TODAY, EQUIPMENTS)

    system_prompt, user_prompt = client.generate.call_args[0]
    assert "equipment_keys" in system_prompt
    assert "water_heater:1" in user_prompt
    assert "Cumulus" in user_prompt
    assert "copie ce jour sur tous les mercredis" in user_prompt


def test_interpret_rejects_malformed_llm_response():
    client = _mock_client({"status": "ready", "message": ""})  # fields missing

    with patch(
        "ai.services.duplication_interpreter._get_llm_client", return_value=client
    ):
        with pytest.raises(DRFValidationError):
            interpret_equipment_duplication_instruction(
                CONVERSATION, TODAY, EQUIPMENTS
            )
