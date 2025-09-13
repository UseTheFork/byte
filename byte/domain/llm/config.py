from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LLMConfig:
    """LLM domain configuration with validation and defaults."""

    provider: str = "auto"
    model: str = "main"
    temperature: float = 0.1
    max_tokens: Optional[int] = None

    def __post_init__(self):
        """Validate LLM configuration values."""
        if not 0 <= self.temperature <= 2:
            raise ValueError(f"Temperature must be 0-2, got {self.temperature}")

        valid_providers = ["auto", "anthropic", "openai", "gemini"]
        if self.provider not in valid_providers:
            raise ValueError(f"Provider must be one of {valid_providers}")
