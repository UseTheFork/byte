"""Skills domain for skill loading and management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.skills.command.skill_command import SkillCommand
    from byte.skills.schemas import Skill
    from byte.skills.service.skill_loader_service import SkillLoaderService
    from byte.skills.service.skill_tracker_service import SkillTrackerService
    from byte.skills.service_provider import SkillsServiceProvider
    from byte.skills.tools.create_skill_tool import CreateSkillTool
    from byte.skills.tools.load_skill_tool import LoadSkillTool

__all__ = (
    "CreateSkillTool",
    "LoadSkillTool",
    "Skill",
    "SkillCommand",
    "SkillLoaderService",
    "SkillTrackerService",
    "SkillsServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "CreateSkillTool": "tools.create_skill_tool",
    "LoadSkillTool": "tools.load_skill_tool",
    "Skill": "schemas",
    "SkillCommand": "command.skill_command",
    "SkillLoaderService": "service.skill_loader_service",
    "SkillTrackerService": "service.skill_tracker_service",
    "SkillsServiceProvider": "service_provider",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
