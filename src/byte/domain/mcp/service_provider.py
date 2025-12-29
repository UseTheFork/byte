from typing import List, Type

from byte.core import Service, ServiceProvider
from byte.domain.cli import Command
from byte.domain.mcp import MCPService


class MCPServiceProvider(ServiceProvider):
    """Service provider for Model Context Protocol (MCP) integration.

    Usage: `await container.register_provider(MCPServiceProvider())`
    """

    def services(self) -> List[Type[Service]]:
        """Register MCP services with the container.

        Usage: `services = provider.services()`
        """
        return [MCPService]

    def commands(self) -> List[Type[Command]]:
        """Register MCP-related CLI commands.

        Usage: `commands = provider.commands()`
        """
        return []
