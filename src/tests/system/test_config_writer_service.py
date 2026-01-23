"""Test suite for ConfigWriterService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import yaml

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide SystemServiceProvider for config writer tests."""
    from byte.system import SystemServiceProvider

    return [SystemServiceProvider]


@pytest.mark.asyncio
async def test_append_preset_adds_preset_to_config_file(application: Application):
    """Test that append_preset adds a new preset to the config.yaml file."""
    from byte.presets.config import PresetsConfig
    from byte.system import ConfigWriterService

    service = application.make(ConfigWriterService)

    # Create a test preset
    preset = PresetsConfig(
        id="test-preset",
        read_only_files=["file1.py", "file2.py"],
        editable_files=["file3.py"],
        conventions=["convention1.md"],
        prompt="Test prompt",
    )

    # Append the preset
    await service.append_preset(preset)

    # Read the config file and verify the preset was added
    config_path = application.config_path("config.yaml")
    with open(config_path) as f:
        config_data = yaml.safe_load(f)

    # Should have presets key
    assert "presets" in config_data

    # Should contain our preset
    presets = config_data["presets"]
    assert len(presets) > 0

    # Find our preset
    test_preset = next((p for p in presets if p["id"] == "test-preset"), None)
    assert test_preset is not None
    assert test_preset["read_only_files"] == ["file1.py", "file2.py"]
    assert test_preset["editable_files"] == ["file3.py"]
    assert test_preset["conventions"] == ["convention1.md"]
    assert test_preset["prompt"] == "Test prompt"
