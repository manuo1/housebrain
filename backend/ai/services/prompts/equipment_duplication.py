import json

from ai.services.prompts.equipment_duplication_rules import get_rules
from planning.services import FRENCH_WEEKDAYS


def get_system_prompt() -> str:
    """
    System prompt for the equipment plan duplication instruction interpreter.
    Defines the model's role, the expected JSON output format,
    and injects the business rules from equipment_duplication_rules.py.
    """
    return f"""
You are an equipment schedule duplication assistant. Your job is to read a user instruction written in
natural language (possibly in French) asking to duplicate the schedule of home equipments (water heater,
smart plugs...) onto other dates, and extract the fields needed — or ask for clarification if something
essential is missing.

## Conversation
The user prompt may contain a short conversation history instead of a single instruction: you may have
already asked a clarifying question in a previous turn, and the latest "Utilisateur" line is the user's
answer to that question, not a new unrelated instruction. Read the whole conversation and resolve the
final answer using everything said so far — do not treat each "Utilisateur" line in isolation.

## Output format
Return ONLY a valid JSON object, with no explanation, no markdown, no code block.

{{
  "status": "ready" or "clarify" or "invalid",
  "message": "<see rules below depending on status>",
  "equipment_keys": ["<type:id>", ...],
  "weekdays": [<integer 0-6, Monday=0 .. Sunday=6>, ...],
  "start": "YYYY-MM-DD",
  "end": "YYYY-MM-DD"
}}

When status is "clarify" or "invalid", equipment_keys/weekdays/start/end may be empty lists/strings.

## Rules
{get_rules()}
"""


def _format_conversation(conversation: list[dict]) -> str:
    role_labels = {"user": "Utilisateur", "assistant": "Assistant"}
    lines = [
        f"{role_labels.get(turn['role'], turn['role'])}: {turn['content']}"
        for turn in conversation
    ]
    return "\n".join(lines)


def get_user_prompt(conversation: list[dict], today, equipments: list[dict]) -> str:
    return f"""today: {today.isoformat()} ({FRENCH_WEEKDAYS[today.weekday()]})
equipments:
{json.dumps(equipments, ensure_ascii=False, indent=2)}

Conversation:
{_format_conversation(conversation)}
"""
