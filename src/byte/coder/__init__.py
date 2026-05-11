from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.coder.agents.coder_agent_node import CoderAgentNode
    from byte.coder.commands.coder_command import CoderCommand
    from byte.coder.service_provider import CoderServiceProvider
    from byte.coder.workflows.coder_workflow import CoderWorkflow


__all__ = (
    "CoderAgentNode",
    "CoderCommand",
    "CoderServiceProvider",
    "CoderWorkflow",
)

_dynamic_imports = {
    # keep-sorted start
    "CoderAgentNode": "agents.coder_agent_node",
    "CoderCommand": "commands.coder_command",
    "CoderServiceProvider": "service_provider",
    "CoderWorkflow": "workflows.coder_workflow",
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
