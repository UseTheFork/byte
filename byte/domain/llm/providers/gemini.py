import os
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI

from byte.domain.llm.service import LLMService


class GeminiLLMService(LLMService):
    """Google Gemini LLM service implementation.

    Provides access to Google's Gemini 1.5 Pro and Flash models with
    configurations optimized for code generation tasks. Requires
    GOOGLE_API_KEY environment variable for authentication.
    Usage: `service = GeminiLLMService(container)` -> Gemini-powered AI functionality
    """

    def get_model_config(self) -> Dict[str, Dict[str, Any]]:
        """Return Gemini model configurations for code-focused tasks.

        Main model uses Gemini 1.5 Pro for complex reasoning and code generation,
        while weak model uses Gemini 1.5 Flash for faster, lighter operations.
        Usage: Called internally to configure model instances
        """
        return {
            "main": {
                "model": "gemini-1.5-pro",
                "temperature": 0,  # Deterministic for consistent code output
                "max_tokens": None,  # No limit for complex code generation
                "max_retries": 2,
            },
            "weak": {
                "model": "gemini-1.5-flash",
                "temperature": 0.3,  # Slightly creative for varied responses
                "max_tokens": 2000,  # Reasonable limit for simpler tasks
                "max_retries": 2,
            },
        }

    def _create_model(self, model_name: str, **kwargs) -> ChatGoogleGenerativeAI:
        """Create Google Gemini model instance with specified configuration.

        Usage: Called internally when model is first requested
        """
        return ChatGoogleGenerativeAI(model=model_name, **kwargs)

    def is_available(self) -> bool:
        """Check if Google API key is configured for service availability.

        Usage: `if service.is_available():` -> verify Gemini can be used
        """
        return bool(os.getenv("GOOGLE_API_KEY"))
