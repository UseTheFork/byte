from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.tools.base_tool import BaseTool
    from byte.tools.schemas import ToolResult
    from byte.tools.service.tool_registry_service import ToolRegistryService
    from byte.tools.service_provider import ToolsServiceProvider

__all__ = (
    "BaseTool",
    "ToolRegistryService",
    "ToolResult",
    "ToolsServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "BaseTool": "BaseTool",
    "ToolRegistryService": "service.tool_registry_service",
    "ToolResult": "schemas",
    "ToolsServiceProvider": "service_provider",
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
