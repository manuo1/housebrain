from abc import ABC, abstractmethod


class LLMClient(ABC):
    """
    Abstract interface for LLM clients.
    Implement this class to add a new LLM provider.
    """

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a prompt to the LLM and return the raw text response.

        Args:
            system_prompt: Instructions for the model (role, format, constraints)
            user_prompt: The user's request

        Returns:
            Raw text response from the model
        """
        pass
