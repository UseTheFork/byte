import os
from typing import Any, Dict

from langchain_anthropic import ChatAnthropic

from byte.domain.llm.service import LLMService


class AnthropicLLMService(LLMService):
    """Anthropic Claude LLM service implementation.

    Provides access to Claude 3.5 Sonnet and Haiku models optimized for
    code generation and analysis. Claude excels at following instructions
    precisely and generating high-quality code with proper formatting.
    Usage: `service = AnthropicLLMService(container)` -> Claude-powered AI functionality
    """

    def get_model_config(self) -> Dict[str, Dict[str, Any]]:
        """Return Claude model configurations for optimal code generation.

        Main model uses Claude 3.5 Sonnet for complex reasoning and code tasks,
        while weak model uses Claude 3.5 Haiku for faster, simpler operations.
        Usage: Called internally to configure model instances
        """
        return {
            "main": {
                "model": "claude-3-5-sonnet-20241022",
                # Claude works well with default parameters for code generation
            },
            "weak": {
                "model": "claude-3-5-haiku-20241022",
                # Haiku is fast and efficient for simpler tasks
            },
        }

    def _create_model(self, model_name: str, **kwargs) -> ChatAnthropic:
        """Create Anthropic Claude model instance with specified configuration.

        Usage: Called internally when model is first requested
        """
        return ChatAnthropic(model=model_name, **kwargs)

    def is_available(self) -> bool:
        """Check if Anthropic API key is configured for service availability.

        Usage: `if service.is_available():` -> verify Claude can be used
        """
        return bool(os.getenv("ANTHROPIC_API_KEY"))
