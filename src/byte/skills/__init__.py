"""Skills domain for skill loading and management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.skills.agents.skill_creator_agent_node import SkillCreatorAgentNode
    from byte.skills.command.skill_command import SkillCommand
    from byte.skills.schemas import Skill
    from byte.skills.service.skill_loader_service import SkillLoaderService
    from byte.skills.service_provider import SkillsServiceProvider
    from byte.skills.tools.add_skill_reference_tool import AddSkillReferenceTool
    from byte.skills.tools.create_skill_tool import CreateSkillTool
    from byte.skills.tools.edit_skill_tool import EditSkillTool
    from byte.skills.tools.load_skill_reference_tool import LoadSkillReferenceTool
    from byte.skills.tools.load_skill_tool import LoadSkillTool
    from byte.skills.workflows.create_skill_workflow import CreateSkillWorkflow

__all__ = (
    "AddSkillReferenceTool",
    "CreateSkillTool",
    "CreateSkillWorkflow",
    "EditSkillTool",
    "LoadSkillReferenceTool",
    "LoadSkillTool",
    "Skill",
    "SkillCommand",
    "SkillCreatorAgentNode",
    "SkillLoaderService",
    "SkillsServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "AddSkillReferenceTool": "tools.add_skill_reference_tool",
    "CreateSkillTool": "tools.create_skill_tool",
    "CreateSkillWorkflow": "workflows.create_skill_workflow",
    "EditSkillTool": "tools.edit_skill_tool",
    "LoadSkillReferenceTool": "tools.load_skill_reference_tool",
    "LoadSkillTool": "tools.load_skill_tool",
    "Skill": "schemas",
    "SkillCommand": "command.skill_command",
    "SkillCreatorAgentNode": "agents.skill_creator_agent_node",
    "SkillLoaderService": "service.skill_loader_service",
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
