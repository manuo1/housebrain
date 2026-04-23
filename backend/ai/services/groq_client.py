import logging

from ai.services.llm_client import LLMClient
from django.conf import settings
from groq import Groq

logger = logging.getLogger("django")

# Model used: llama-3.3-70b is Groq's best free model for structured JSON generation.
# Alternatives: "mixtral-8x7b-32768", "llama3-8b-8192" (faster, less accurate)
GROQ_MODEL = "llama-3.3-70b-versatile"


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
        except Exception as e:
            logger.error("Groq API error: %s", e)
            raise
