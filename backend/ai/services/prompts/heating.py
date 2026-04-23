import json

from ai.services.prompts.heating_rules import get_rules


def get_system_prompt() -> str:
    """
    System prompt for heating plan modification.
    Defines the model's role, the expected JSON output format,
    and injects the business rules from heating_rules.py.
    """
    return f"""
You are a heating schedule assistant. Your job is to modify a home heating plan based on a user instruction written in natural language (possibly in French).

## Your task
- Read the current heating plan provided by the user
- Apply the requested modification following the rules below
- Return the updated plan in the exact same JSON format

## Output format
Return ONLY a valid JSON object, with no explanation, no markdown, no code block.
The JSON must strictly follow this structure:

{{
  "date": "YYYY-MM-DD",
  "rooms": [
    {{
      "room_id": <integer>,
      "name": "<string>",
      "slots": [
        {{
          "start": "HH:MM",
          "end": "HH:MM",
          "type": "<temp|onoff>",
          "value": <number if type=temp, "on" or "off" if type=onoff>
        }}
      ]
    }}
  ]
}}

## Rules
{get_rules()}
"""


def get_user_prompt(instruction: str, plan: dict) -> str:
    """
    User prompt for heating plan modification.

    Args:
        instruction: The user's natural language instruction
        plan: The current heating plan as a dict (dailyPlan.raw from the frontend)

    Returns:
        The formatted user prompt string
    """
    return f"""Current heating plan:
{json.dumps(plan, ensure_ascii=False, indent=2)}

Instruction: {instruction}
"""
