from byte.core.config.config import BaseConfig


class ModelConfig(BaseConfig):
    """Configuration for the main LLM model used for primary tasks."""

    model: str = ""
    api_key: str = ""

    temperature: float = 0.1

    max_input_tokens: int = 200000
    max_output_tokens: int = 1024

    input_cost_per_token: float = 0
    output_cost_per_token: float = 0

    cache_creation_input_token_cost: float = 0
    cache_read_input_token_cost: float = 0


class LLMConfig(BaseConfig):
    """LLM domain configuration with validation and defaults."""

    model: str = ""
    main: ModelConfig = ModelConfig()
    weak: ModelConfig = ModelConfig()
