"""Agent domain for AI agent implementations and orchestration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.workflow.service.workflow_service import WorkflowService
    from byte.workflow.service_provider import WorkflowServiceProvider
    from byte.workflow.workflows.base import BaseWorkflow

__all__ = (
    "BaseWorkflow",
    "WorkflowService",
    "WorkflowServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "BaseWorkflow": "workflows.base",
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
