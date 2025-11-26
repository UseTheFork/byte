from pathlib import Path

import yaml

from byte.core.config.config import BYTE_CONFIG_FILE
from byte.core.service.base_service import Service
from byte.domain.presets.config import PresetsConfig


class ConfigWriterService(Service):
    """Service for writing preset configurations to the YAML config file.

    Handles reading, updating, and writing the config.yaml file to persist
    preset configurations across sessions.
    Usage: `await service.append_preset(preset_config)`
    """

    async def boot(self) -> None:
        """Initialize the config writer service."""
        self.config_path: Path = BYTE_CONFIG_FILE

    async def append_preset(self, preset: PresetsConfig) -> None:
        """Append a new preset to the config.yaml file.

        Reads the existing config, adds the new preset to the presets list,
        and writes the updated config back to the file.
        Usage: `await service.append_preset(new_preset)`
        """
        # Read existing config
        with open(self.config_path) as f:
            config_data = yaml.safe_load(f) or {}

        # Ensure presets key exists
        if "presets" not in config_data:
            config_data["presets"] = []

        # Convert preset to dict for YAML serialization
        preset_dict = preset.model_dump(exclude_none=True)

        # Append new preset
        config_data["presets"].append(preset_dict)

        # Write updated config back to file
        with open(self.config_path, "w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, sort_keys=False)
