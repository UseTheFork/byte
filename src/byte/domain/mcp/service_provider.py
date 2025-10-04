from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.mcp.command.mcp_tool_command import MCPToolCommand
from byte.domain.mcp.service.mcp_service import MCPService


class MCPServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [MCPService]

    def commands(self) -> List[Type[Command]]:
        """"""
        return [MCPToolCommand]
