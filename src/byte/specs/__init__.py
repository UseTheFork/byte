"""Specs domain for spec loading and management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.specs.agents.spec_creator_agent_node import SpecCreatorAgentNode
    from byte.specs.agents.spec_task_creator_agent_node import SpecTaskCreatorAgentNode
    from byte.specs.command.quick_spec_command import QuickSpecCommand
    from byte.specs.command.refractor_command import RefractorCommand
    from byte.specs.command.spec_command import SpecCommand
    from byte.specs.command.spec_execute_command import SpecExecuteCommand
    from byte.specs.schemas import Spec, SpecTask
    from byte.specs.service.spec_loader_service import SpecLoaderService
    from byte.specs.service_provider import SpecsServiceProvider
    from byte.specs.tools.create_spec_tool import CreateSpecTool
    from byte.specs.tools.create_task_tool import CreateTaskTool
    from byte.specs.tools.edit_task_tool import EditTaskTool
    from byte.specs.workflows.create_quick_spec_workflow import CreateQuickSpecWorkflow
    from byte.specs.workflows.create_refractor_workflow import CreateRefractorWorkflow
    from byte.specs.workflows.create_spec_task_workflow import CreateSpecTaskWorkflow
    from byte.specs.workflows.create_spec_workflow import CreateSpecWorkflow

__all__ = (
    "CreateQuickSpecWorkflow",
    "CreateRefractorWorkflow",
    "CreateSpecTaskWorkflow",
    "CreateSpecTool",
    "CreateSpecWorkflow",
    "CreateTaskTool",
    "EditTaskTool",
    "QuickSpecCommand",
    "RefractorCommand",
    "Spec",
    "SpecCommand",
    "SpecCreatorAgentNode",
    "SpecExecuteCommand",
    "SpecLoaderService",
    "SpecTask",
    "SpecTaskCreatorAgentNode",
    "SpecsServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "CreateQuickSpecWorkflow": "workflows.create_quick_spec_workflow",
    "CreateRefractorWorkflow": "workflows.create_refractor_workflow",
    "CreateSpecTaskWorkflow": "workflows.create_spec_task_workflow",
    "CreateSpecTool": "tools.create_spec_tool",
    "CreateSpecWorkflow": "workflows.create_spec_workflow",
    "CreateTaskTool": "tools.create_task_tool",
    "EditTaskTool": "tools.edit_task_tool",
    "QuickSpecCommand": "command.quick_spec_command",
    "RefractorCommand": "command.refractor_command",
    "Spec": "schemas",
    "SpecCommand": "command.spec_command",
    "SpecCreatorAgentNode": "agents.spec_creator_agent_node",
    "SpecExecuteCommand": "command.spec_execute_command",
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
