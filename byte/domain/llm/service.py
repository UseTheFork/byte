from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from byte.container import Container


class LLMService(ABC):
    """Base LLM service that all providers extend.

    Provides a unified interface for different LLM providers (OpenAI, Anthropic, etc.)
    with model caching and configuration management. Enables provider-agnostic
    AI functionality throughout the application.
    Usage: `service = OpenAILLMService(container)` -> provider-specific implementation
    """

    def __init__(self, container: Optional["Container"] = None):
        self.container = container
        # Cache model instances to avoid repeated initialization overhead
        self._models: Dict[str, Any] = {}

    @abstractmethod
    def get_model_config(self) -> Dict[str, Dict[str, Any]]:
        """Return model configuration for this provider.

        Usage: Override in subclass -> `{"main": {"model": "gpt-4", ...}, "weak": {...}}`
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available (API keys, etc.).

        Usage: `if service.is_available():` -> verify provider can be used
        """
        pass

    @abstractmethod
    def _create_model(self, model_name: str, **kwargs) -> Any:
        """Create the actual model instance using provider-specific class.

        Usage: Override in subclass -> `return ChatOpenAI(model=model_name, **kwargs)`
        """
        pass

    def get_model(self, model_type: str = "main") -> Any:
        """Get a model instance with lazy initialization and caching.

        Retrieves cached model or creates new one based on configuration,
        reducing initialization overhead for frequently used models.
        Usage: `model = service.get_model("main")` -> cached LangChain model instance
        """
        if model_type not in self._models:
            config = self.get_model_config()
            if model_type not in config:
                raise ValueError(
                    f"Model type '{model_type}' not available for {self.__class__.__name__}"
                )

            model_config = config[model_type].copy()
            model_name = model_config.pop("model")
            self._models[model_type] = self._create_model(model_name, **model_config)

        return self._models[model_type]

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
