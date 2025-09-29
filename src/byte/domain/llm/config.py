from byte.core.config.config import BaseConfig


class ModelConfig(BaseConfig):
    """Configuration for the main LLM model used for primary tasks."""

    model: str = ""
    temperature: float = 0.1
    max_tokens: int = 1024


class LLMConfig(BaseConfig):
    """LLM domain configuration with validation and defaults."""

    model: str = ""
    main: ModelConfig = ModelConfig()
    weak: ModelConfig = ModelConfig()
