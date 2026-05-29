"""Harness domain — bootstrapping utilities for agents."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.harness.agents.harness_agent_node import HarnessAgentNode
    from byte.harness.service_provider import HarnessServiceProvider
    from byte.harness.tools.bootstrap_agent_tool import BootstrapAgentTool
    from byte.harness.tools.bootstrap_skills_files_tool import BootstrapSkillsFilesTool
    from byte.harness.tools.bootstrap_skills_tool import BootstrapSkillsTool
    from byte.harness.workflows.agent_harness_workflow import AgentHarnessWorkflow


__all__ = (
    "AgentHarnessWorkflow",
    "BootstrapAgentTool",
    "BootstrapSkillsFilesTool",
    "BootstrapSkillsTool",
    "HarnessAgentNode",
    "HarnessServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "AgentHarnessWorkflow": "workflows.agent_harness_workflow",
    "BootstrapAgentTool": "tools.bootstrap_agent_tool",
    "BootstrapSkillsFilesTool": "tools.bootstrap_skills_files_tool",
    "BootstrapSkillsTool": "tools.bootstrap_skills_tool",
    "HarnessAgentNode": "agents.harness_agent_node",
    "HarnessServiceProvider": "service_provider",
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
