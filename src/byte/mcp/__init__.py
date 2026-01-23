"""MCP domain for Model Context Protocol integration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.mcp.command.mcp_tool_command import MCPToolCommand
    from byte.domain.mcp.config import AgentToolFilter, MCPConnection, MCPServer, ToolCommandFilter
    from byte.domain.mcp.service.mcp_service import MCPService
    from byte.domain.mcp.service_provider import MCPServiceProvider

__all__ = (
    "AgentToolFilter",
    "MCPConnection",
    "MCPServer",
    "MCPService",
    "MCPServiceProvider",
    "MCPToolCommand",
    "ToolCommandFilter",
)

_dynamic_imports = {
    # keep-sorted start
    "AgentToolFilter": "config",
    "MCPConnection": "config",
    "MCPServer": "config",
    "MCPService": "service.mcp_service",
    "MCPServiceProvider": "service_provider",
    "MCPToolCommand": "command.mcp_tool_command",
    "ToolCommandFilter": "config",
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
