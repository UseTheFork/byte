"""Test suite for LLMService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from byte import EventType
from byte.llm import LLMService, ModelSchema

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide LLMServiceProvider for LLM service tests."""
    from byte.llm import LLMServiceProvider

    return [LLMServiceProvider]


@pytest.mark.asyncio
async def test_boot_configures_anthropic_schema(application: Application):
    """Test that boot configures AnthropicSchema when anthropic is selected."""

    # Set anthropic as the model
    application["config"].llm.providers.anthropic.enable = True
    application["config"].llm.providers.anthropic.api_key = "test-key"

    service = application.make(LLMService)
    service.boot()

    assert isinstance(service._main_schema, ModelSchema)
    assert service._main_schema.model_class == ChatAnthropic
    assert service._main_schema.provider.api_key == "test-key"


@pytest.mark.asyncio
async def test_boot_uses_default_when_provider_name_set(application: Application):
    """Test that boot uses default model when provider name is set as model."""

    # Set provider name as the model
    application["config"].llm.providers.anthropic.enable = True
    application["config"].llm.providers.anthropic.api_key = "test-key"
    application["config"].llm.main_model.model = "anthropic"

    application["config"].llm.providers.openai.enable = True
    application["config"].llm.providers.openai.api_key = "test-key"
    application["config"].llm.weak_model.model = "openai"

    service = application.make(LLMService)
    service.boot()

    assert service._main_schema.params.model == "claude-sonnet-4-5"
    assert service._weak_schema.params.model == "gpt-5-mini"


@pytest.mark.asyncio
async def test_boot_configures_openai_schema(application: Application, monkeypatch):
    """Test that boot configures OpenAiSchema when openai is selected."""
    from byte.llm import LLMService

    # Set openai as the model
    application["config"].llm.providers.anthropic.enable = False
    application["config"].llm.providers.gemini.enable = False
    application["config"].llm.providers.openai.enable = True
    application["config"].llm.providers.openai.api_key = "test-key"

    service = application.make(LLMService)
    service.boot()

    assert isinstance(service._main_schema, ModelSchema)
    assert service._main_schema.model_class == ChatOpenAI
    assert service._main_schema.provider.api_key == "test-key"


@pytest.mark.asyncio
async def test_boot_configures_gemini_schema(application: Application):
    """Test that boot configures GoogleSchema when gemini is selected."""
    from byte.llm import LLMService

    # Set gemini as the model
    application["config"].llm.providers.anthropic.enable = False
    application["config"].llm.providers.openai.enable = False
    application["config"].llm.providers.gemini.enable = True
    application["config"].llm.providers.gemini.api_key = "test-key"

    service = application.make(LLMService)
    service.boot()

    assert isinstance(service._main_schema, ModelSchema)
    assert service._main_schema.model_class == ChatGoogleGenerativeAI
    assert service._main_schema.provider.api_key == "test-key"


@pytest.mark.asyncio
async def test_boot_copies_provider_params(application: Application):
    """Test that boot copies provider_params from config."""
    from byte.llm import LLMService

    # Set provider params
    application["config"].llm.main_model.extra_params = {"custom_param": "value"}

    service = application.make(LLMService)
    service.boot()

    assert service._main_schema.extra_params == {"custom_param": "value"}


@pytest.mark.asyncio
async def test_get_model_returns_main_model_by_default(application: Application):
    """Test that get_model returns main model when no type specified."""
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_model()

    assert model is not None
    assert hasattr(model, "invoke")


@pytest.mark.asyncio
async def test_get_model_returns_weak_model_when_specified(application: Application):
    """Test that get_model returns weak model when type is 'weak'."""
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_model("weak")

    assert model is not None
    assert hasattr(model, "invoke")


@pytest.mark.asyncio
async def test_get_model_uses_correct_model_class(application: Application):
    """Test that get_model instantiates the correct model class."""
    from langchain_anthropic import ChatAnthropic

    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_model()

    assert isinstance(model, ChatAnthropic)


@pytest.mark.asyncio
async def test_get_model_applies_model_params(application: Application):
    """Test that get_model applies params from model schema."""
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_model()

    # Check that model has expected params
    assert isinstance(model, ChatAnthropic)
    assert service._main_schema.params.model == "claude-sonnet-4-5"


@pytest.mark.asyncio
async def test_get_model_applies_max_tokens_constraint(application: Application):
    """Test that get_model applies max_tokens from constraints."""
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_model()

    assert model.max_tokens == 64000


@pytest.mark.asyncio
async def test_get_model_merges_provider_params(application: Application):
    """Test that get_model merges provider_params from schema."""
    from byte.llm import LLMService

    application["config"].llm.providers.anthropic.extra_params = {"custom_header": "value"}

    service = application.make(LLMService)
    service.boot()
    model = service.get_model()

    # Provider params should be passed to model
    assert hasattr(model, "custom_header") or model.model_kwargs.get("custom_header") == "value"


@pytest.mark.asyncio
async def test_get_model_kwargs_override_provider_params(application: Application):
    """Test that kwargs passed to get_model override provider_params."""
    from byte.llm import LLMService

    application["config"].llm.main_model.extra_params = {"param": "original"}

    service = application.make(LLMService)
    service.boot()
    model = service.get_model(param="overridden")

    # Kwargs should override provider params
    assert model.model_kwargs.get("param") == "overridden"


@pytest.mark.asyncio
async def test_get_main_model_returns_main_model(application: Application):
    """Test that get_main_model returns the main model."""
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_main_model()

    assert model is not None
    assert isinstance(model, ChatAnthropic)


@pytest.mark.asyncio
async def test_get_weak_model_returns_weak_model(application: Application):
    """Test that get_weak_model returns the weak model."""

    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    model = service.get_weak_model()

    assert model is not None
    assert isinstance(model, ChatAnthropic)


@pytest.mark.asyncio
async def test_add_reinforcement_hook_adds_eager_reinforcement(application: Application):
    """Test that add_reinforcement_hook adds eager reinforcement messages."""
    from byte import Payload
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    payload = Payload(event_type=EventType.TEST, data={"mode": "main"})

    result = await service.add_reinforcement_hook(payload)

    reinforcement = result.get("reinforcement", [])
    assert len(reinforcement) > 0
    assert any("scope" in msg.lower() for msg in reinforcement)


@pytest.mark.asyncio
async def test_add_reinforcement_hook_adds_lazy_reinforcement(application: Application):
    """Test that add_reinforcement_hook adds lazy reinforcement messages."""
    from byte import Payload
    from byte.llm import LLMService, ReinforcementMode

    service = application.make(LLMService)
    service.boot()

    # Modify the weak model to use lazy reinforcement
    service._weak_schema.behavior.reinforcement_mode = ReinforcementMode.LAZY

    payload = Payload(event_type=EventType.TEST, data={"mode": "weak"})

    result = await service.add_reinforcement_hook(payload)

    reinforcement = result.get("reinforcement", [])
    assert len(reinforcement) > 0
    assert any("diligent" in msg.lower() for msg in reinforcement)


@pytest.mark.asyncio
async def test_add_reinforcement_hook_skips_none_mode(application: Application):
    """Test that add_reinforcement_hook skips reinforcement for NONE mode."""
    from byte import Payload
    from byte.llm import LLMService, ReinforcementMode

    service = application.make(LLMService)
    service.boot()

    # Modify the main model to use no reinforcement
    service._main_schema.behavior.reinforcement_mode = ReinforcementMode.NONE

    payload = Payload(event_type=EventType.TEST, data={"mode": "main"})

    result = await service.add_reinforcement_hook(payload)

    reinforcement = result.get("reinforcement", [])
    assert len(reinforcement) == 0


@pytest.mark.asyncio
async def test_add_reinforcement_hook_uses_main_mode_by_default(application: Application):
    """Test that add_reinforcement_hook uses main mode when mode not specified."""
    from byte import Payload
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()

    payload = Payload(event_type=EventType.TEST)

    result = await service.add_reinforcement_hook(payload)

    # Should use main model's reinforcement (eager for anthropic)
    reinforcement = result.get("reinforcement", [])
    assert len(reinforcement) > 0


@pytest.mark.asyncio
async def test_add_reinforcement_hook_extends_existing_reinforcement(application: Application):
    """Test that add_reinforcement_hook extends existing reinforcement list."""
    from byte import Payload
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    payload = Payload(event_type=EventType.TEST, data={"mode": "main", "reinforcement": ["existing message"]})

    result = await service.add_reinforcement_hook(payload)

    reinforcement = result.get("reinforcement", [])
    assert "existing message" in reinforcement
    assert len(reinforcement) > 1


@pytest.mark.asyncio
async def test_add_reinforcement_hook_returns_payload(application: Application):
    """Test that add_reinforcement_hook returns the modified payload."""
    from byte import Payload
    from byte.llm import LLMService

    service = application.make(LLMService)
    service.boot()
    payload = Payload(event_type=EventType.TEST)

    result = await service.add_reinforcement_hook(payload)

    assert isinstance(result, Payload)
    assert result.event_type == EventType.TEST
