import logging
import re

from django.conf import settings
from groq import APIError, Groq, RateLimitError
from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.llm_client import LLMClient

logger = logging.getLogger("django")

# Model used: openai/gpt-oss-120b, Groq's recommended replacement for the
# deprecated llama-3.3-70b-versatile (decommissioned August 16, 2026 per Groq's
# notice). Also cheaper and faster on Groq's own pricing/speed comparison.
# Alternatives: "openai/gpt-oss-20b" (faster, less accurate), "qwen/qwen3-32b"
GROQ_MODEL = "openai/gpt-oss-120b"


def _parse_retry_delay(error_message: str) -> str | None:
    """
    Extracts the retry delay from a Groq rate limit error message.
    Example input: "Please try again in 58m46.848s."
    Returns a human-readable string like "58 minutes" or "45 secondes".
    """
    # Match patterns like "58m46s", "2m3.5s", "45.2s", "3m"
    match = re.search(r"try again in (?:(\d+)m)?(?:[\d.]+s)?", error_message)
    if match:
        minutes = match.group(1)
        if minutes:
            return f"{minutes} minute{'s' if int(minutes) > 1 else ''}"
        # Only seconds — round up to 1 minute
        return "moins d'une minute"
    return None


class GroqClient(LLMClient):
    """
    LLM client implementation using Groq.
    """

    def __init__(self):
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in settings")
        self.client = Groq(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    # System message: defines the model's role, output format and rules
                    {"role": "system", "content": system_prompt},
                    # User message: the instruction + current heating plan
                    {"role": "user", "content": user_prompt},
                ],
                # Low temperature for deterministic, structured JSON output
                temperature=0.2,
                # Sufficient for a full heating plan with 10 rooms and multiple slots
                max_tokens=4096,
            )
            return response.choices[0].message.content

        except RateLimitError as e:
            logger.warning("Groq rate limit reached: %s", e)
            retry_delay = _parse_retry_delay(str(e))
            if retry_delay:
                message = f"Le service IA a atteint sa limite quotidienne. Réessayez dans {retry_delay}."
            else:
                message = "Le service IA a atteint sa limite quotidienne. Réessayez plus tard."
            raise DRFValidationError(message)

        except APIError as e:
            logger.error("Groq API error: %s", e)
            raise DRFValidationError(
                "Le service IA est temporairement indisponible. Réessayez dans quelques instants."
            )

        except Exception as e:
            logger.error("Unexpected Groq error: %s", e)
            raise DRFValidationError(
                "Une erreur inattendue s'est produite lors de la communication avec le service IA."
            )
