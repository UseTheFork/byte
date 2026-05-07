from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
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
    )

__all__ = (
    "AddGovernanceRuleTool",
    "AddPrincipleTool",
    "AddSectionItemTool",
    "AddSectionTool",
    "Constitution",
    "ConstitutionGovernanceRule",
    "ConstitutionItem",
    "ConstitutionMeta",
    "ConstitutionPrinciple",
    "ConstitutionSection",
    "ConstitutionService",
    "ConstitutionServiceProvider",
    "DeleteGovernanceRuleTool",
    "DeletePrincipleTool",
    "DeleteSectionItemTool",
    "DeleteSectionTool",
)

_dynamic_imports = {
    # keep-sorted start
    "AddGovernanceRuleTool": "tools",
    "AddPrincipleTool": "tools",
    "AddSectionItemTool": "tools",
    "AddSectionTool": "tools",
    "Constitution": "models",
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
