from ai.services.prompt_builder import build_prompt


def test_build_prompt_returns_system_and_user_prompt_as_tuple():
    assert build_prompt("system instructions", "user request") == (
        "system instructions",
        "user request",
    )
