import json

from ai.services.prompts.duplication_rules import get_rules

FRENCH_WEEKDAYS = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]


def get_system_prompt() -> str:
    """
    System prompt for the heating plan duplication instruction interpreter.
    Defines the model's role, the expected JSON output format,
    and injects the business rules from duplication_rules.py.
    """
    return f"""
You are a heating schedule duplication assistant. Your job is to read a user instruction written in
natural language (possibly in French) asking to duplicate a heating plan onto other dates, and extract
the fields needed — or ask for clarification if something essential is missing.

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
  "room_ids": [<integer>, ...],
  "weekdays": [<integer 0-6, Monday=0 .. Sunday=6>, ...],
  "start": "YYYY-MM-DD",
  "end": "YYYY-MM-DD"
}}

When status is "clarify" or "invalid", room_ids/weekdays/start/end may be empty lists/strings.

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


def get_user_prompt(conversation: list[dict], today, rooms: list[dict]) -> str:
    return f"""today: {today.isoformat()} ({FRENCH_WEEKDAYS[today.weekday()]})
rooms:
{json.dumps(rooms, ensure_ascii=False, indent=2)}

Conversation:
{_format_conversation(conversation)}
"""
