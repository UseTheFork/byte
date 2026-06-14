from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.documentation.agents.documentation_agent_node import DocumentationAgentNode
    from byte.documentation.commands.documentation_command import DocumentationCommand
    from byte.documentation.config import DocumentationConfig
    from byte.documentation.service_provider import DocumentationServiceProvider
    from byte.documentation.workflows.documentation_workflow import DocumentationWorkflow


__all__ = (
    "DocumentationAgentNode",
    "DocumentationCommand",
    "DocumentationConfig",
    "DocumentationServiceProvider",
    "DocumentationWorkflow",
)

_dynamic_imports = {
    # keep-sorted start
    "DocumentationAgentNode": "agents.documentation_agent_node",
    "DocumentationCommand": "commands.documentation_command",
    "DocumentationConfig": "config",
    "DocumentationServiceProvider": "service_provider",
    "DocumentationWorkflow": "workflows.documentation_workflow",
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
