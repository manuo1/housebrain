from core.constants import TerminalColor


def colored_text(text: str, color: TerminalColor) -> str:
    """Add color to terminal output."""
    return f"\033[{color.value}m{text}\033[0m"
