from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.ask.agents.ask_agent_node import AskAgentNode
    from byte.ask.commands.ask_command import AskCommand
    from byte.ask.service_provider import AskServiceProvider
    from byte.ask.workflows.ask_workflow import AskWorkflow


__all__ = (
    "AskAgentNode",
    "AskCommand",
    "AskServiceProvider",
    "AskWorkflow",
)

_dynamic_imports = {
    # keep-sorted start
    "AskServiceProvider": "service_provider",
    "AskCommand": "commands.ask_command",
    "AskAgentNode": "agents.ask_agent_node",
    "AskWorkflow": "workflows.ask_workflow",
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
