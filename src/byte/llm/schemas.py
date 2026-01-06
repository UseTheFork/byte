from enum import Enum
from typing import Any, Dict, Type

from langchain.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class ReinforcementMode(str, Enum):
    """Strategy for adding reinforcement messages to model prompts.

    Controls whether and how strongly to reinforce instructions to ensure
    the model follows guidelines and produces desired output format.
    """

    NONE = "none"
    LAZY = "lazy"
    EAGER = "eager"


class ModelConstraints(BaseModel):
    """Operational constraints and cost specifications for an LLM model.

    Defines the capacity limits and economic factors that constrain model usage,
    including token limits and per-token costs for various operations.
    Usage: `constraints = ModelConstraints(max_input_tokens=200000, max_output_tokens=64000)`
    """

    max_input_tokens: int = 0
    max_output_tokens: int = 0

    input_cost_per_token: float = 0
    output_cost_per_token: float = 0

    input_cost_per_token_cached: float = 0
    cache_read_input_token_cost: float = 0


class ModelParams(BaseModel):
    """Configuration parameters for LLM model initialization.

    Defines the runtime parameters used to configure and authenticate with
    an LLM model, including model selection and behavioral settings.
    Usage: `params = ModelParams(model="claude-sonnet-4-5", api_key="...", temperature=0.1)`
    """

    model: str = ""
    temperature: float = 0.1
    stream_usage: bool | None = None


class ModelBehavior(BaseModel):
    """Behavioral configuration for model prompt engineering and output handling.

    Defines ByteSmith-specific behaviors that control how prompts are constructed
    and how the model is guided, separate from LangChain model parameters.
    Usage: `behavior = ModelBehavior(reinforcement_mode=ReinforcementMode.EAGER)`
    """

    reinforcement_mode: ReinforcementMode = ReinforcementMode.NONE


class ModelSchema(BaseModel):
    """Configuration for the main LLM model used for primary tasks."""

    params: ModelParams = Field(default_factory=ModelParams)
    constraints: ModelConstraints = Field(default_factory=ModelConstraints)
    behavior: ModelBehavior = Field(default_factory=ModelBehavior)


class LLMSchema(BaseModel):
    """Base schema for LLM provider configuration with dual-model support.

    Defines the structure for LLM providers that use a main model for complex tasks
    and a weaker model for simpler, cost-effective operations.
    Usage: `schema = LLMSchema(api_key="...", main=ModelSchema(...), weak=ModelSchema(...))`
    """

    model_class: Type[BaseChatModel]
    api_key: str = ""
    provider_params: Dict[str, Any] = Field(default_factory=dict)
    main: ModelSchema = Field(default_factory=ModelSchema)
    weak: ModelSchema = Field(default_factory=ModelSchema)


class AnthropicSchema(LLMSchema):
    """Anthropic-specific LLM configuration with Claude model defaults.

    Provides pre-configured settings for Anthropic's Claude models, including
    Claude Sonnet for main tasks and Claude Haiku for lightweight operations.
    Usage: `schema = AnthropicSchema(api_key="...")` -> defaults to Claude models
    """

    model_class: Type[BaseChatModel] = ChatAnthropic
    main: ModelSchema = Field(
        default_factory=lambda: ModelSchema(
            params=ModelParams(
                model="claude-sonnet-4-5",
                temperature=0.1,
            ),
            constraints=ModelConstraints(
                max_input_tokens=200000,
                max_output_tokens=64000,
                input_cost_per_token=0.000003,
                output_cost_per_token=0.000015,
            ),
            behavior=ModelBehavior(
                reinforcement_mode=ReinforcementMode.EAGER,
            ),
        )
    )
    weak: ModelSchema = Field(
        default_factory=lambda: ModelSchema(
            params=ModelParams(
                model="claude-3-5-haiku-latest",
                temperature=0.1,
            ),
            constraints=ModelConstraints(
                max_input_tokens=200000,
                max_output_tokens=8192,
                input_cost_per_token=(0.80 / 1000000),
                output_cost_per_token=(4 / 1000000),
            ),
            behavior=ModelBehavior(
                reinforcement_mode=ReinforcementMode.NONE,
            ),
        )
    )


class OpenAiSchema(LLMSchema):
    """OpenAI-specific LLM configuration with GPT model defaults.

    Provides pre-configured settings for OpenAI's GPT models, including
    GPT-5 for main tasks and GPT-5-mini for lightweight operations with caching support.
    Usage: `schema = OpenAiSchema(api_key="...")` -> defaults to GPT models
    """

    model_class: Type[BaseChatModel] = ChatOpenAI
    main: ModelSchema = Field(
        default_factory=lambda: ModelSchema(
            params=ModelParams(
                model="gpt-5",
                temperature=0.1,
                stream_usage=True,
            ),
            constraints=ModelConstraints(
                max_input_tokens=400000,
                max_output_tokens=128000,
                input_cost_per_token=(1.25 / 1000000),
                output_cost_per_token=(10 / 1000000),
                input_cost_per_token_cached=(0.125 / 1000000),
            ),
            behavior=ModelBehavior(
                reinforcement_mode=ReinforcementMode.NONE,
            ),
        )
    )
    weak: ModelSchema = Field(
        default_factory=lambda: ModelSchema(
            params=ModelParams(
                model="gpt-5-mini",
                temperature=0.1,
                stream_usage=True,
            ),
            constraints=ModelConstraints(
                max_input_tokens=400000,
                max_output_tokens=128000,
                input_cost_per_token=(0.25 / 1000000),
                output_cost_per_token=(2 / 1000000),
                input_cost_per_token_cached=(0.025 / 1000000),
            ),
            behavior=ModelBehavior(
                reinforcement_mode=ReinforcementMode.NONE,
            ),
        )
    )


class GoogleSchema(LLMSchema):
    """Google-specific LLM configuration with Gemini model defaults.

    Provides pre-configured settings for Google's Gemini models, including
    Gemini 2.5 Pro for main tasks and Gemini 2.5 Flash for lightweight operations with caching support.
    Usage: `schema = GoogleSchema(api_key="...")` -> defaults to Gemini models
    """

    model_class: Type[BaseChatModel] = ChatGoogleGenerativeAI
    main: ModelSchema = Field(
        default_factory=lambda: ModelSchema(
            params=ModelParams(
                model="gemini-2.5-pro",
                temperature=0.1,
            ),
            constraints=ModelConstraints(
                max_input_tokens=200000,
                max_output_tokens=65536,
                input_cost_per_token=(2.5 / 1000000),
                output_cost_per_token=(15 / 1000000),
                input_cost_per_token_cached=(0.25 / 1000000),
            ),
            behavior=ModelBehavior(
                reinforcement_mode=ReinforcementMode.NONE,
            ),
        )
    )
    weak: ModelSchema = Field(
        default_factory=lambda: ModelSchema(
            params=ModelParams(
                model="gemini-2.5-flash-lite",
                temperature=0.1,
            ),
            constraints=ModelConstraints(
                max_input_tokens=200000,
                max_output_tokens=65536,
                input_cost_per_token=(0.3 / 1000000),
                output_cost_per_token=(2.5 / 1000000),
                input_cost_per_token_cached=(0.03 / 1000000),
            ),
            behavior=ModelBehavior(
                reinforcement_mode=ReinforcementMode.NONE,
            ),
        )
    )
