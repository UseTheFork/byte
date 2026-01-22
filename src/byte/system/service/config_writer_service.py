import yaml

from byte import Service
from byte.presets.config import PresetsConfig


class ConfigWriterService(Service):
    """Service for writing preset configurations to the YAML config file.

    Handles reading, updating, and writing the config.yaml file to persist
    preset configurations across sessions.
    Usage: `await service.append_preset(preset_config)`
    """

    async def append_preset(self, preset: PresetsConfig) -> None:
        """Append a new preset to the config.yaml file.

        Reads the existing config, adds the new preset to the presets list,
        and writes the updated config back to the file.
        Usage: `await service.append_preset(new_preset)`
        """

        config_path = self.app.config_path("config.yaml")

        # Read existing config
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}

        # Ensure presets key exists
        if "presets" not in config_data:
            config_data["presets"] = []

        # Convert preset to dict for YAML serialization
        preset_dict = preset.model_dump(exclude_none=True)

        # Append new preset
        config_data["presets"].append(preset_dict)

        # Write updated config back to file
        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=True, sort_keys=False)
