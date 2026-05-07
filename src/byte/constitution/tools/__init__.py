from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.constitution.tools.add_governance_rule_tool import AddGovernanceRuleTool
    from byte.constitution.tools.add_principle_tool import AddPrincipleTool
    from byte.constitution.tools.add_section_item_tool import AddSectionItemTool
    from byte.constitution.tools.add_section_tool import AddSectionTool
    from byte.constitution.tools.delete_governance_rule_tool import DeleteGovernanceRuleTool
    from byte.constitution.tools.delete_principle_tool import DeletePrincipleTool
    from byte.constitution.tools.delete_section_item_tool import DeleteSectionItemTool
    from byte.constitution.tools.delete_section_tool import DeleteSectionTool

__all__ = (
    "AddGovernanceRuleTool",
    "AddPrincipleTool",
    "AddSectionItemTool",
    "AddSectionTool",
    "DeleteGovernanceRuleTool",
    "DeletePrincipleTool",
    "DeleteSectionItemTool",
    "DeleteSectionTool",
)

_dynamic_imports = {
    # keep-sorted start
    "AddGovernanceRuleTool": "add_governance_rule_tool",
    "AddPrincipleTool": "add_principle_tool",
    "AddSectionItemTool": "add_section_item_tool",
    "AddSectionTool": "add_section_tool",
    "DeleteGovernanceRuleTool": "delete_governance_rule_tool",
    "DeletePrincipleTool": "delete_principle_tool",
    "DeleteSectionItemTool": "delete_section_item_tool",
    "DeleteSectionTool": "delete_section_tool",
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
