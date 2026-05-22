"""Specs domain for spec loading and management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.specs.agents.spec_creator_agent_node import SpecCreatorAgentNode
    from byte.specs.agents.spec_task_creator_agent_node import SpecTaskCreatorAgentNode
    from byte.specs.command.spec_command import SpecCommand
    from byte.specs.command.spec_task_command import SpecTaskCommand
    from byte.specs.schemas import Spec, SpecTask
    from byte.specs.service.spec_loader_service import SpecLoaderService
    from byte.specs.service_provider import SpecsServiceProvider
    from byte.specs.tools.create_spec_tool import CreateSpecTool
    from byte.specs.tools.create_task_tool import CreateTaskTool
    from byte.specs.workflows.create_spec_phase_workflow import CreateSpecPhaseWorkflow
    from byte.specs.workflows.create_spec_workflow import CreateSpecWorkflow

__all__ = (
    "CreateSpecPhaseWorkflow",
    "CreateSpecTool",
    "CreateSpecWorkflow",
    "CreateTaskTool",
    "Spec",
    "SpecCommand",
    "SpecCreatorAgentNode",
    "SpecLoaderService",
    "SpecTask",
    "SpecTaskCommand",
    "SpecTaskCreatorAgentNode",
    "SpecsServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "SpecTaskCommand": "command.spec_task_command",
    "CreateTaskTool": "tools.create_task_tool",
    "CreateSpecPhaseWorkflow": "workflows.create_spec_phase_workflow",
    "CreateSpecTool": "tools.create_spec_tool",
    "CreateSpecWorkflow": "workflows.create_spec_workflow",
    "Spec": "schemas",
    "SpecCommand": "command.spec_command",
    "SpecCreatorAgentNode": "agents.spec_creator_agent_node",
    "SpecLoaderService": "service.spec_loader_service",
    "SpecTask": "schemas",
    "SpecTaskCreatorAgentNode": "agents.spec_task_creator_agent_node",
    "SpecsServiceProvider": "service_provider",
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
