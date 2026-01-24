from pathlib import Path

import requests
import yaml

API_URL = "https://models.dev/api.json"


def extract_model_info(model_data: dict, provider: str) -> dict | None:
    """Extract relevant model information for ByteSmith configuration.

    Usage: `info = extract_model_info(model_data, provider)` -> returns dict with cost and limit info or None if tool_call is false
    """
    if not model_data.get("tool_call", False):
        return None

    modalities = model_data.get("modalities", {})
    output_modalities = modalities.get("output", [])
    if "text" not in output_modalities:
        return None

    cost = model_data.get("cost", {})
    limit = model_data.get("limit", {})

    print(model_data)

    return {
        "id": model_data.get("id", ""),
        "name": model_data.get("name", ""),
        "provider": provider,
        "cost": {
            "input": cost.get("input", 0),
            "output": cost.get("output", 0),
            "cache_read": cost.get("cache_read", 0),
        },
        "limit": {
            "context": limit.get("context", 0),
            "output": limit.get("output", 0),
        },
    }


def main():
    """Fetch model data from models.dev API and generate resource file.

    Usage: `python -m scripts.update_models` -> creates models_data.yaml
    """
    response = requests.get(API_URL)
    data = response.json()

    providers = ["anthropic", "openai", "google"]
    models_resource = {}

    for provider in providers:
        if provider not in data:
            continue

        provider_models = data[provider].get("models", {})

        for model_id, model_data in provider_models.items():
            model_info = extract_model_info(model_data, provider)
            if model_info is not None:
                models_resource[model_id] = model_info

    output_path = Path(__file__).parent.parent / "byte" / "llm" / "resources" / "models_data.yaml"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        yaml.dump(models_resource, f, default_flow_style=False, sort_keys=False)

    print(f"Generated models data at: {output_path}")


if __name__ == "__main__":
    main()
