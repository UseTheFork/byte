"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.workflow.command.ask_command import AskCommand
    from byte.workflow.command.coder_command import CoderCommand
    from byte.workflow.service.workflow_service import WorkflowService
    from byte.workflow.service_provider import WorkflowServiceProvider
    from byte.workflow.workflows.ask_workflow import AskWorkflow
    from byte.workflow.workflows.base import BaseWorkflow
    from byte.workflow.workflows.coder_workflow import CoderWorkflow


__all__ = (
    "AskCommand",
    "AskWorkflow",
    "BaseWorkflow",
    "CoderCommand",
    "CoderWorkflow",
    "WorkflowService",
    "WorkflowServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "AskCommand": "command.ask_command",
    "AskWorkflow": "workflows.ask_workflow",
    "BaseWorkflow": "workflows.base",
    "CoderCommand": "command.coder_command",
    "CoderWorkflow": "workflows.coder_workflow",
    "WorkflowService": "service.workflow_service",
    "WorkflowServiceProvider": "service_provider",
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
