from datetime import datetime
from unittest.mock import patch

from django.utils import timezone

from ai.services.prompts.equipment import get_system_prompt, get_user_prompt
from ai.services.prompts.equipment_rules import get_rules


def test_get_system_prompt_contains_output_format_and_business_rules():
    prompt = get_system_prompt()

    assert '"success": true or false' in prompt
    assert '"equipments"' in prompt
    # Business rules from equipment_rules.py must be injected
    assert get_rules() in prompt


def test_get_user_prompt_contains_time_plan_and_instruction():
    fake_now = timezone.make_aware(datetime(2026, 1, 1, 14, 30))

    with patch("ai.services.prompts.equipment.timezone.now", return_value=fake_now):
        prompt = get_user_prompt(
            instruction="allume le chauffe-eau",
            plan={"equipments": [{"type": "water_heater", "id": 1, "name": "Cuve"}]},
        )

    assert "14:30" in prompt
    assert "allume le chauffe-eau" in prompt
    assert '"type": "water_heater"' in prompt
    assert '"name": "Cuve"' in prompt
