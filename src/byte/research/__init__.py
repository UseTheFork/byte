from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.research.agents.research_agent_node import ResearchAgentNode
    from byte.research.commands.research_command import ResearchCommand
    from byte.research.service_provider import ResearchServiceProvider
    from byte.research.workflows.research_workflow import ResearchWorkflow


__all__ = (
    "ResearchAgentNode",
    "ResearchCommand",
    "ResearchServiceProvider",
    "ResearchWorkflow",
)

_dynamic_imports = {
    # keep-sorted start
    "ResearchServiceProvider": "service_provider",
    "ResearchCommand": "commands.research_command",
    "ResearchAgentNode": "agents.research_agent_node",
    "ResearchWorkflow": "workflows.research_workflow",
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
