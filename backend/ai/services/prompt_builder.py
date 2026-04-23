def build_prompt(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    """
    Generic prompt assembler.
    Returns the system and user prompts as a tuple ready to be passed to any LLM client.

    Args:
        system_prompt: The system instructions (role, format, constraints)
        user_prompt: The user request with context data

    Returns:
        (system_prompt, user_prompt) tuple
    """
    return system_prompt, user_prompt
