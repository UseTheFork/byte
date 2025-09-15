from typing import TYPE_CHECKING, Any, Dict

from langchain_anthropic import ChatAnthropic

from byte.core.config.configurable import Configurable
from byte.core.mixins.bootable import Bootable
from byte.domain.llm.config import LLMConfig

if TYPE_CHECKING:
    pass


class LLMService(Bootable, Configurable):
    """Base LLM service that all providers extend.

    Provides a unified interface for different LLM providers (OpenAI, Anthropic, etc.)
    with model caching and configuration management. Enables provider-agnostic
    AI functionality throughout the application.
    Usage: `service = OpenAILLMService(container)` -> provider-specific implementation
    """

    _models: Dict[str, Any] = {}
    _config: LLMConfig

    def get_model(self, model_type: str = "main", **kwargs) -> Any:
        """Get a model instance with lazy initialization and caching.

        Retrieves cached model or creates new one based on configuration,
        reducing initialization overhead for frequently used models.
        Usage: `model = service.get_model("main")` -> cached LangChain model instance
        """

        if self._config.base == "sonnet" and model_type == "main":
            return ChatAnthropic(**self._config.main.__dict__, **kwargs)

        elif self._config.base == "sonnet" and model_type == "weak":
            return ChatAnthropic(**self._config.weak.__dict__, **kwargs)

    def get_main_model(self) -> Any:
        """Convenience method for accessing the primary model.

        Usage: `main_model = service.get_main_model()` -> high-capability model
        """
        return self.get_model("main")

    def get_weak_model(self) -> Any:
        """Convenience method for accessing the secondary model.

        Usage: `weak_model = service.get_weak_model()` -> faster/cheaper model
        """
        return self.get_model("weak")
