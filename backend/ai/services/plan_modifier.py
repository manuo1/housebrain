import json
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.groq_client import GroqClient
from ai.services.prompt_builder import build_prompt
from ai.services.prompts.equipment import (
    get_system_prompt as get_equipment_system_prompt,
)
from ai.services.prompts.equipment import (
    get_user_prompt as get_equipment_user_prompt,
)
from ai.services.prompts.heating import get_system_prompt, get_user_prompt
from planning.models import SchedulePattern

logger = logging.getLogger("django")


def _get_llm_client():
    """
    Returns the active LLM client.
    Swap this function to change provider (e.g. return AnthropicClient()).
    """
    return GroqClient()


def _parse_llm_response(raw_response: str) -> dict:
    """
    Parses the raw LLM text response into a dict.
    Strips markdown code blocks if the model added them despite instructions.
    """
    text = raw_response.strip()

    # Strip markdown code block if present (defensive)
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(
            "Failed to parse LLM response as JSON: %s\nRaw response: %s",
            e,
            raw_response,
        )
        raise DRFValidationError("Le modèle IA n'a pas retourné un format valide.")


def _check_success(parsed: dict) -> None:
    """
    Checks the success field returned by the LLM.
    Raises DRFValidationError with the reason if success is False.
    """
    success = parsed.get("success")

    if success is False:
        reason = parsed.get("reason") or "La modification n'a pas pu être appliquée."
        logger.warning("LLM reported failure: %s", reason)
        raise DRFValidationError(reason)

    if success is not True:
        logger.warning("LLM response missing 'success' field: %s", parsed)
        raise DRFValidationError("Le modèle IA n'a pas retourné un format valide.")


def _infer_slot_type(slot: dict) -> dict:
    """
    Infers and injects the 'type' field if missing.
    Groq sometimes omits 'type' when recopying existing slots from the input plan,
    because dailyPlan.raw from the frontend does not include this field.

    Rules:
    - value is "on" or "off" → type "onoff"
    - value is numeric (int, float, or numeric string) → type "temp", value cast to float
    """
    if "type" in slot:
        return slot

    value = slot.get("value")

    if str(value).lower() in ("on", "off"):
        slot["type"] = "onoff"
    else:
        slot["type"] = "temp"
        try:
            slot["value"] = float(str(value))
        except (ValueError, TypeError):
            pass  # Let _validate_plan catch the invalid value

    return slot


def _normalize_plan(plan: dict) -> dict:
    """
    Normalizes the plan returned by the LLM before validation.
    Currently: infers missing 'type' fields on all slots.
    """
    for room in plan.get("rooms", []):
        room["slots"] = [_infer_slot_type(slot) for slot in room.get("slots", [])]
    return plan


def _validate_plan(plan: dict) -> None:
    """
    Validates the plan returned by the LLM.
    Checks structure and runs SchedulePattern.clean() on each room's slots
    to enforce all business rules (overlap, duration, type consistency, etc.).
    """
    if not isinstance(plan, dict):
        raise DRFValidationError("Le plan retourné par l'IA est invalide.")

    if "rooms" not in plan or not isinstance(plan["rooms"], list):
        raise DRFValidationError("Le plan retourné par l'IA ne contient pas de pièces.")

    for room in plan["rooms"]:
        room_name = room.get("name", f"room_id={room.get('room_id')}")
        slots = room.get("slots", [])

        try:
            SchedulePattern.get_or_create_from_slots(slots)
        except DjangoValidationError as e:
            logger.warning("Invalid slots for room %s: %s", room_name, e)
            raise DRFValidationError(
                f"Le plan généré contient des créneaux invalides pour '{room_name}' : {e.message}"
            )


def modify_heating_plan(instruction: str, plan: dict) -> dict:
    """
    Main entry point for AI-based heating plan modification.

    Args:
        instruction: The user's natural language instruction
        plan: The current heating plan as a dict (dailyPlan.raw from the frontend)

    Returns:
        The modified heating plan as a dict, validated and ready to be returned to the frontend
    """
    system_prompt, user_prompt = build_prompt(
        get_system_prompt(),
        get_user_prompt(instruction, plan),
    )

    client = _get_llm_client()
    logger.info(
        "Sending heating plan modification request to LLM - instruction: %s",
        instruction,
    )

    raw_response = client.generate(system_prompt, user_prompt)
    logger.info("LLM raw response: %s", raw_response)

    parsed = _parse_llm_response(raw_response)
    _check_success(parsed)

    parsed.pop("success", None)
    parsed.pop("reason", None)

    _normalize_plan(parsed)
    _validate_plan(parsed)

    return parsed


def _normalize_equipment_plan(plan: dict) -> dict:
    """
    Equipment counterpart of _normalize_plan: the plan key is "equipments"
    instead of "rooms", so the heating version can't be reused as is.
    """
    for equipment in plan.get("equipments", []):
        equipment["slots"] = [
            _infer_slot_type(slot) for slot in equipment.get("slots", [])
        ]
    return plan


def _validate_equipment_plan(plan: dict) -> None:
    """
    Equipment counterpart of _validate_plan: same SchedulePattern checks
    (overlap, duration, type consistency), applied per equipment.
    """
    if not isinstance(plan, dict):
        raise DRFValidationError("Le plan retourné par l'IA est invalide.")

    if "equipments" not in plan or not isinstance(plan["equipments"], list):
        raise DRFValidationError(
            "Le plan retourné par l'IA ne contient pas d'équipements."
        )

    for equipment in plan["equipments"]:
        equipment_name = equipment.get(
            "name", f"{equipment.get('type')}_id={equipment.get('id')}"
        )
        slots = equipment.get("slots", [])

        try:
            SchedulePattern.get_or_create_from_slots(slots)
        except DjangoValidationError as e:
            logger.warning("Invalid slots for equipment %s: %s", equipment_name, e)
            raise DRFValidationError(
                f"Le plan généré contient des créneaux invalides pour '{equipment_name}' : {e.message}"
            )


def modify_equipment_plan(instruction: str, plan: dict) -> dict:
    """
    Main entry point for AI-based equipment plan modification.

    Args:
        instruction: The user's natural language instruction
        plan: The current equipment plan as a dict (dailyPlan.raw from the frontend)

    Returns:
        The modified equipment plan as a dict, validated and ready to be returned to the frontend
    """
    system_prompt, user_prompt = build_prompt(
        get_equipment_system_prompt(),
        get_equipment_user_prompt(instruction, plan),
    )

    client = _get_llm_client()
    logger.info(
        "Sending equipment plan modification request to LLM - instruction: %s",
        instruction,
    )

    raw_response = client.generate(system_prompt, user_prompt)
    logger.info("LLM raw response: %s", raw_response)

    parsed = _parse_llm_response(raw_response)
    _check_success(parsed)

    parsed.pop("success", None)
    parsed.pop("reason", None)

    _normalize_equipment_plan(parsed)
    _validate_equipment_plan(parsed)

    return parsed
