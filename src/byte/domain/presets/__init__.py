"""Presets domain for saving and loading context configurations."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.presets.command.load_preset_command import LoadPresetCommand
    from byte.domain.presets.command.save_preset_command import SavePresetCommand
    from byte.domain.presets.config import PresetsConfig
    from byte.domain.presets.service_provider import PresetsProvider

__all__ = (
    "LoadPresetCommand",
    "PresetsConfig",
    "PresetsProvider",
    "SavePresetCommand",
)

_dynamic_imports = {
    "LoadPresetCommand": "command.load_preset_command",
    "PresetsConfig": "config",
    "PresetsProvider": "service_provider",
    "SavePresetCommand": "command.save_preset_command",
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
