from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMService(ABC):
    """Base LLM service that all providers extend."""

    def __init__(self, container):
        self.container = container
        self._models = {}

    @abstractmethod
    def get_model_config(self) -> Dict[str, Dict[str, Any]]:
        """Return model configuration for this provider."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available (API keys, etc.)."""
        pass

    @abstractmethod
    def _create_model(self, model_name: str, **kwargs):
        """Create the actual model instance using provider-specific class."""
        pass

    def get_model(self, model_type: str = "main"):
        """Get a model instance. Caches models for reuse."""
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

    def get_main_model(self):
        """Convenience method for main model."""
        return self.get_model("main")

    def get_weak_model(self):
        """Convenience method for weak model."""
        return self.get_model("weak")
