from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.constitution.agents.constitution_agent_node import ConstitutionAgentNode
    from byte.constitution.command.constitution_command import ConstitutionCommand
    from byte.constitution.command.initialize_command import InitializeCommand
    from byte.constitution.models import (
        Constitution,
        ConstitutionGovernanceRule,
        ConstitutionItem,
        ConstitutionMeta,
        ConstitutionPrinciple,
        ConstitutionSection,
    )
    from byte.constitution.service.constitution_service import ConstitutionService
    from byte.constitution.service_provider import ConstitutionServiceProvider
    from byte.constitution.tools import (
        AddGovernanceRuleTool,
        AddPrincipleTool,
        AddSectionItemTool,
        AddSectionTool,
        DeleteGovernanceRuleTool,
        DeletePrincipleTool,
        DeleteSectionItemTool,
        DeleteSectionTool,
        UpdateMetaTool,
    )
    from byte.constitution.workflows.constitution_workflow import ConstitutionWorkflow

__all__ = (
    "AddGovernanceRuleTool",
    "AddPrincipleTool",
    "AddSectionItemTool",
    "AddSectionTool",
    "Constitution",
    "ConstitutionAgentNode",
    "ConstitutionCommand",
    "ConstitutionGovernanceRule",
    "ConstitutionItem",
    "ConstitutionMeta",
    "ConstitutionPrinciple",
    "ConstitutionSection",
    "ConstitutionService",
    "ConstitutionServiceProvider",
    "ConstitutionWorkflow",
    "DeleteGovernanceRuleTool",
    "DeletePrincipleTool",
    "DeleteSectionItemTool",
    "DeleteSectionTool",
    "InitializeCommand",
    "UpdateMetaTool",
)

_dynamic_imports = {
    # keep-sorted start
    "ConstitutionWorkflow": "workflows.constitution_workflow",
    "ConstitutionAgentNode": "agents.constitution_agent_node",
    "AddGovernanceRuleTool": "tools",
    "AddPrincipleTool": "tools",
    "AddSectionItemTool": "tools",
    "AddSectionTool": "tools",
    "Constitution": "models",
    "ConstitutionCommand": "command.constitution_command",
    "ConstitutionGovernanceRule": "models",
    "ConstitutionItem": "models",
    "ConstitutionMeta": "models",
    "ConstitutionPrinciple": "models",
    "ConstitutionSection": "models",
    "ConstitutionService": "service.constitution_service",
    "ConstitutionServiceProvider": "service_provider",
    "DeleteGovernanceRuleTool": "tools",
    "DeletePrincipleTool": "tools",
    "DeleteSectionItemTool": "tools",
    "DeleteSectionTool": "tools",
    "InitializeCommand": "command.initialize_command",
    "UpdateMetaTool": "tools",
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
