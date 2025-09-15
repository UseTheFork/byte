from pydantic.dataclasses import dataclass

from byte.core.config.schema import BaseConfig


@dataclass(frozen=True)
class ModelConfig(BaseConfig):
    """Configuration for the main LLM model used for primary tasks."""

    model: str = ""
    temperature: float = 0.1


@dataclass(frozen=True)
class LLMConfig(BaseConfig):
    """LLM domain configuration with validation and defaults."""

    base: str = ""
    main: ModelConfig = ModelConfig()
    weak: ModelConfig = ModelConfig()
