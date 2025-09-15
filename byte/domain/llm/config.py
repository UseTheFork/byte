from byte.core.config.schema import BaseConfig


class ModelConfig(BaseConfig):
    """Configuration for the main LLM model used for primary tasks."""

    model: str = ""
    temperature: float = 0.1


class LLMConfig(BaseConfig):
    """LLM domain configuration with validation and defaults."""

    base: str = ""
    main: ModelConfig = ModelConfig()
    weak: ModelConfig = ModelConfig()
