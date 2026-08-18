import json
import logging
from datetime import date

from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.groq_client import GroqClient
from ai.services.prompt_builder import build_prompt
from ai.services.prompts.duplication import get_system_prompt, get_user_prompt
from heating.api.selectors import get_daily_heating_plan

logger = logging.getLogger("django")

VALID_STATUSES = {"ready", "clarify", "invalid"}


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

    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(
            "Failed to parse duplication LLM response as JSON: %s\nRaw response: %s",
            e,
            raw_response,
        )
        raise DRFValidationError("Le modèle IA n'a pas retourné un format valide.")


def _validate_llm_shape(parsed: dict) -> None:
    """
    Validates the raw shape returned by the LLM (fields present, correct types).
    Does not validate date coherence or business rules.
    """
    if not isinstance(parsed, dict):
        raise DRFValidationError("Réponse IA invalide.")

    status = parsed.get("status")
    if status not in VALID_STATUSES:
        logger.warning("Duplication LLM returned an unknown status: %s", parsed)
        raise DRFValidationError("Réponse IA invalide (status manquant ou inconnu).")

    if not isinstance(parsed.get("message"), str):
        raise DRFValidationError("Réponse IA invalide (message manquant).")

    if status != "ready":
        return

    for key in ("room_ids", "weekdays"):
        if not isinstance(parsed.get(key), list):
            raise DRFValidationError(f"Réponse IA invalide (champ '{key}' manquant ou mal formé).")

    for key in ("start", "end"):
        if not isinstance(parsed.get(key), str):
            raise DRFValidationError(f"Réponse IA invalide (champ '{key}' manquant ou mal formé).")


def get_rooms_for_date(source_date: date) -> list[dict]:
    """
    Returns the rooms (room_id, name) that have a heating plan on source_date.
    Slots are dropped — the LLM only needs to resolve room names, not their content.
    """
    return [
        {"room_id": room["room_id"], "name": room["name"]}
        for room in get_daily_heating_plan(source_date)
    ]


def interpret_duplication_instruction(conversation: list[dict], source_date: date, today: date) -> dict:
    """
    Main entry point for AI-based duplication instruction interpretation.

    The LLM only extracts fields (room_ids/weekdays/start/end) from the instruction and asks
    clarifying questions when something's missing. No date-coherence validation, no occurrence
    computation, no recap message — that's a separate step, not implemented yet.

    Args:
        conversation: List of {"role": "user"|"assistant", "content": str} turns, oldest first.
            A single-turn instruction is just a one-item list: [{"role": "user", "content": "..."}]
        source_date: The day currently displayed (already saved), used to resolve room names
        today: The real current date

    Returns:
        A dict: {"status": "ready"|"clarify"|"invalid", "message": str,
                 "room_ids": [...], "weekdays": [...], "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
    """
    rooms = get_rooms_for_date(source_date)

    system_prompt, user_prompt = build_prompt(
        get_system_prompt(),
        get_user_prompt(conversation, today, rooms),
    )

    client = _get_llm_client()
    logger.info(
        "Sending duplication interpretation request to LLM - conversation: %s",
        conversation,
    )

    raw_response = client.generate(system_prompt, user_prompt)
    logger.info("Duplication LLM raw response: %s", raw_response)

    parsed = _parse_llm_response(raw_response)
    _validate_llm_shape(parsed)

    return parsed
