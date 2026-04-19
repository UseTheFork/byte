from typing import TYPE_CHECKING, Dict, Optional

from byte.llm import ModelConstraints, ModelSchema
from byte.support import Service, Yaml

if TYPE_CHECKING:
    pass


class LLMRegistryService(Service):
    """Central read-only registry for LLM models loaded from models_data.yaml."""

    def boot(self):
        """Load LLM models from models_data.yaml on boot."""

        models_data_path = self.app.app_path("llm/resources/models_data.yaml")
        raw_models = Yaml.load_as_dict(models_data_path)
        self._models: Dict[str, ModelSchema] = {}

        for model_id, model_data in raw_models.items():
            constraints = ModelConstraints(
                max_input_tokens=model_data["limit"]["context"],
                max_output_tokens=model_data["limit"]["output"],
                input_cost_per_token=model_data["cost"]["input"],
                output_cost_per_token=model_data["cost"]["output"],
                input_cost_per_token_cached=model_data["cost"]["cache_read"],
            )
            model = ModelSchema(
                model=model_id,
                provider=model_data["provider"],
                constraints=constraints,
            )
            self._models[model_id] = model

    def get_model(self, model_id: str) -> Optional[ModelSchema]:
        """Retrieve a registered model by ID.

        Args:
            model_id: The model identifier (e.g., "claude-sonnet-4-5")

        Returns:
            Model data dictionary or None if not found
        """
        return self._models.get(model_id)

    def get_all_models(self) -> Dict[str, ModelSchema]:
        """Retrieve all registered models.

        Returns:
            Dictionary of all models keyed by model ID
        """
        return self._models.copy()
