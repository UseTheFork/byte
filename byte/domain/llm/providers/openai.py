import os
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from byte.domain.llm.service import LLMService


class OpenAILLMService(LLMService):
    """OpenAI LLM service implementation using GPT models.

    Provides access to OpenAI's GPT-4 and GPT-3.5 models with optimized
    configurations for code generation and analysis tasks. Requires
    OPENAI_API_KEY environment variable for authentication.
    Usage: `service = OpenAILLMService(container)` -> OpenAI-powered AI functionality
    """

    def get_model_config(self) -> Dict[str, Dict[str, Any]]:
        """Return OpenAI model configurations optimized for code tasks.

        Main model uses GPT-4o for high-quality code generation and analysis,
        while weak model uses GPT-3.5-turbo for faster, simpler operations.
        Usage: Called internally to configure model instances
        """
        return {
            "main": {
                "model": "gpt-4o",
                "temperature": 0,  # Deterministic output for code generation
                "max_tokens": None,  # No limit for complex code tasks
                "timeout": None,  # Allow time for complex reasoning
                "max_retries": 2,
            },
            "weak": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,  # Slightly creative for varied responses
                "max_tokens": 2000,  # Limit for simpler tasks
                "max_retries": 2,
            },
        }

    def _create_model(self, model_name: str, **kwargs) -> ChatOpenAI:
        """Create OpenAI ChatGPT model instance with specified configuration.

        Usage: Called internally when model is first requested
        """
        return ChatOpenAI(model=model_name, **kwargs)

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured for service availability.

        Usage: `if service.is_available():` -> verify OpenAI can be used
        """
        return bool(os.getenv("OPENAI_API_KEY"))
