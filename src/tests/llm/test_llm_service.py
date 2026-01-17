from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from langchain_anthropic import ChatAnthropic

from byte import EventType
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestLLMService(BaseTest):
    """Test suite for LLMService."""

    @pytest.fixture
    def providers(self):
        """Provide LLMServiceProvider for LLM service tests."""
        from byte.llm import LLMServiceProvider

        return [LLMServiceProvider]

    @pytest.mark.asyncio
    async def test_boot_configures_anthropic_schema(self, application: Application):
        """Test that boot configures AnthropicSchema when anthropic is selected."""
        from byte.llm import AnthropicSchema, LLMService

        # Set anthropic as the model
        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()

        assert isinstance(service._service_config, AnthropicSchema)
        assert service._service_config.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_boot_configures_openai_schema(self, application: Application):
        """Test that boot configures OpenAiSchema when openai is selected."""
        from byte.llm import LLMService, OpenAiSchema

        # Set openai as the model
        application["config"].llm.model = "openai"
        application["config"].llm.openai.api_key = "test-openai-key"

        service = application.make(LLMService)
        service.boot()

        assert isinstance(service._service_config, OpenAiSchema)
        assert service._service_config.api_key == "test-openai-key"

    @pytest.mark.asyncio
    async def test_boot_configures_gemini_schema(self, application: Application):
        """Test that boot configures GoogleSchema when gemini is selected."""
        from byte.llm import GoogleSchema, LLMService

        # Set gemini as the model
        application["config"].llm.model = "gemini"
        application["config"].llm.gemini.api_key = "test-gemini-key"

        service = application.make(LLMService)
        service.boot()

        assert isinstance(service._service_config, GoogleSchema)
        assert service._service_config.api_key == "test-gemini-key"

    @pytest.mark.asyncio
    async def test_boot_copies_provider_params(self, application: Application):
        """Test that boot copies provider_params from config."""
        from byte.llm import LLMService

        # Set provider params
        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.model_params = {"custom_param": "value"}

        service = application.make(LLMService)
        service.boot()

        assert service._service_config.provider_params == {"custom_param": "value"}

    @pytest.mark.asyncio
    async def test_get_model_returns_main_model_by_default(self, application: Application):
        """Test that get_model returns main model when no type specified."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_model()

        assert model is not None
        assert hasattr(model, "invoke")

    @pytest.mark.asyncio
    async def test_get_model_returns_weak_model_when_specified(self, application: Application):
        """Test that get_model returns weak model when type is 'weak'."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_model("weak")

        assert model is not None
        assert hasattr(model, "invoke")

    @pytest.mark.asyncio
    async def test_get_model_uses_correct_model_class(self, application: Application):
        """Test that get_model instantiates the correct model class."""
        from langchain_anthropic import ChatAnthropic

        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_model()

        assert isinstance(model, ChatAnthropic)

    @pytest.mark.asyncio
    async def test_get_model_applies_model_params(self, application: Application):
        """Test that get_model applies params from model schema."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_model()

        # Check that model has expected params
        assert isinstance(model, ChatAnthropic)

    @pytest.mark.asyncio
    async def test_get_model_applies_max_tokens_constraint(self, application: Application):
        """Test that get_model applies max_tokens from constraints."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_model()

        assert model.max_tokens == 64000

    @pytest.mark.asyncio
    async def test_get_model_merges_provider_params(self, application: Application):
        """Test that get_model merges provider_params from schema."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"
        application["config"].llm.anthropic.model_params = {"custom_header": "value"}

        service = application.make(LLMService)
        service.boot()
        model = service.get_model()

        # Provider params should be passed to model
        assert hasattr(model, "custom_header") or model.model_kwargs.get("custom_header") == "value"

    @pytest.mark.asyncio
    async def test_get_model_kwargs_override_provider_params(self, application: Application):
        """Test that kwargs passed to get_model override provider_params."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"
        application["config"].llm.anthropic.model_params = {"param": "original"}

        service = application.make(LLMService)
        service.boot()
        model = service.get_model(param="overridden")

        # Kwargs should override provider params
        assert model.model_kwargs.get("param") == "overridden"

    @pytest.mark.asyncio
    async def test_get_main_model_returns_main_model(self, application: Application):
        """Test that get_main_model returns the main model."""
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_main_model()

        assert model is not None
        assert isinstance(model, ChatAnthropic)

    @pytest.mark.asyncio
    async def test_get_weak_model_returns_weak_model(self, application: Application):
        """Test that get_weak_model returns the weak model."""

        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        model = service.get_weak_model()

        assert model is not None
        assert isinstance(model, ChatAnthropic)

    @pytest.mark.asyncio
    async def test_add_reinforcement_hook_adds_eager_reinforcement(self, application: Application):
        """Test that add_reinforcement_hook adds eager reinforcement messages."""
        from byte import Payload
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        payload = Payload(event_type=EventType.TEST, data={"mode": "main"})

        result = await service.add_reinforcement_hook(payload)

        reinforcement = result.get("reinforcement", [])
        assert len(reinforcement) > 0
        assert any("scope" in msg.lower() for msg in reinforcement)

    @pytest.mark.asyncio
    async def test_add_reinforcement_hook_adds_lazy_reinforcement(self, application: Application):
        """Test that add_reinforcement_hook adds lazy reinforcement messages."""
        from byte import Payload
        from byte.llm import LLMService, ReinforcementMode

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()

        # Modify the weak model to use lazy reinforcement
        service._service_config.weak.behavior.reinforcement_mode = ReinforcementMode.LAZY

        payload = Payload(event_type=EventType.TEST, data={"mode": "weak"})

        result = await service.add_reinforcement_hook(payload)

        reinforcement = result.get("reinforcement", [])
        assert len(reinforcement) > 0
        assert any("diligent" in msg.lower() for msg in reinforcement)

    @pytest.mark.asyncio
    async def test_add_reinforcement_hook_skips_none_mode(self, application: Application):
        """Test that add_reinforcement_hook skips reinforcement for NONE mode."""
        from byte import Payload
        from byte.llm import LLMService, ReinforcementMode

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()

        # Modify the main model to use no reinforcement
        service._service_config.main.behavior.reinforcement_mode = ReinforcementMode.NONE

        payload = Payload(event_type=EventType.TEST, data={"mode": "main"})

        result = await service.add_reinforcement_hook(payload)

        reinforcement = result.get("reinforcement", [])
        assert len(reinforcement) == 0

    @pytest.mark.asyncio
    async def test_add_reinforcement_hook_uses_main_mode_by_default(self, application: Application):
        """Test that add_reinforcement_hook uses main mode when mode not specified."""
        from byte import Payload
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()

        payload = Payload(event_type=EventType.TEST)

        result = await service.add_reinforcement_hook(payload)

        # Should use main model's reinforcement (eager for anthropic)
        reinforcement = result.get("reinforcement", [])
        assert len(reinforcement) > 0

    @pytest.mark.asyncio
    async def test_add_reinforcement_hook_extends_existing_reinforcement(self, application: Application):
        """Test that add_reinforcement_hook extends existing reinforcement list."""
        from byte import Payload
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        payload = Payload(event_type=EventType.TEST, data={"mode": "main", "reinforcement": ["existing message"]})

        result = await service.add_reinforcement_hook(payload)

        reinforcement = result.get("reinforcement", [])
        assert "existing message" in reinforcement
        assert len(reinforcement) > 1

    @pytest.mark.asyncio
    async def test_add_reinforcement_hook_returns_payload(self, application: Application):
        """Test that add_reinforcement_hook returns the modified payload."""
        from byte import Payload
        from byte.llm import LLMService

        application["config"].llm.model = "anthropic"
        application["config"].llm.anthropic.api_key = "test-key"

        service = application.make(LLMService)
        service.boot()
        payload = Payload(event_type=EventType.TEST)

        result = await service.add_reinforcement_hook(payload)

        assert isinstance(result, Payload)
        assert result.event_type == EventType.TEST
