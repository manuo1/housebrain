from datetime import date

from ai.services.prompts.equipment_duplication import get_system_prompt, get_user_prompt
from ai.services.prompts.equipment_duplication_rules import get_rules


def test_get_system_prompt_contains_output_format_and_business_rules():
    prompt = get_system_prompt()

    assert '"status": "ready" or "clarify" or "invalid"' in prompt
    assert '"equipment_keys"' in prompt
    # Business rules from equipment_duplication_rules.py must be injected
    assert get_rules() in prompt


def test_get_user_prompt_contains_today_equipments_and_conversation():
    prompt = get_user_prompt(
        conversation=[
            {"role": "user", "content": "copie ce jour sur tous les mercredis"},
            {"role": "assistant", "content": "Jusqu'à quand ?"},
            {"role": "user", "content": "jusqu'au 30 août"},
        ],
        today=date(2026, 8, 15),  # Saturday
        equipments=[{"key": "water_heater:1", "name": "Cumulus"}],
    )

    assert "today: 2026-08-15 (samedi)" in prompt
    assert '"key": "water_heater:1"' in prompt
    assert '"name": "Cumulus"' in prompt
    assert "Utilisateur: copie ce jour sur tous les mercredis" in prompt
    assert "Assistant: Jusqu'à quand ?" in prompt
    assert "Utilisateur: jusqu'au 30 août" in prompt
