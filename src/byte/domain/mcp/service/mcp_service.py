from typing import Dict

from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from byte.core.service.base_service import Service


class MCPService(Service):
    """MCP service for managing Model Context Protocol integrations with agent-specific tool filtering."""

    # Agent type mapping for tool filtering
    AGENT_MAPPING = {
        "ask": "ask",
        "coder": "coder",
    }

    async def boot(self, **kwargs):
        self._all_tools = {}  # Store filtered tools by agent type
        self._agent_tools = {}  # Store filtered tools by agent type

        # Build connections dict from config
        connections = {}

        for server in self._config.mcp:
            server_config = {"transport": server.connection.transport}

            if server.connection.transport == "stdio":
                server_config["command"] = server.connection.command
                if server.connection.args:
                    server_config["args"] = server.connection.args
            elif server.connection.transport == "streamable_http":
                server_config["url"] = server.connection.url
                if server.connection.headers:
                    server_config["headers"] = server.connection.headers

            connections[server.name] = server_config

        if connections:
            client = MultiServerMCPClient(connections)
            tools = await client.get_tools()

            self._all_tools = tools
            # Filter tools for each agent type based on server configuration
            await self._filter_tools_by_agent(tools)

    async def _filter_tools_by_agent(self, tools):
        """Filter tools for each agent type based on MCP server configuration."""
        # Initialize agent tools dict
        for agent_name in self.AGENT_MAPPING:
            self._agent_tools[agent_name] = []

        # Process each MCP server's agent configuration
        for server in self._config.mcp:
            if not server.agents:
                # If no agent filtering specified, add all tools to all agents
                for agent_name in self.AGENT_MAPPING:
                    self._agent_tools[agent_name].extend(tools)
                continue

            # Apply agent-specific filtering
            for agent_name, filter_config in server.agents.items():
                if agent_name not in self.AGENT_MAPPING:
                    continue

                filtered_tools = []

                if filter_config.include:
                    # If include list specified, only add tools in the include list
                    filtered_tools = [tool for tool in tools if tool.name in filter_config.include]
                elif filter_config.exclude:
                    # If exclude list specified, add all tools except excluded ones
                    filtered_tools = [tool for tool in tools if tool.name not in filter_config.exclude]
                else:
                    # No filtering specified for this agent, add all tools
                    filtered_tools = tools

                self._agent_tools[agent_name].extend(filtered_tools)

    def get_tools_for_agent(self, agent_name: str):
        """Get filtered tools for a specific agent type."""
        return self._agent_tools.get(agent_name, [])

    def get_all_tools(self):
        """Get all available MCP tools without filtering.

        Usage: `tools = mcp_service.get_all_tools()`
        """
        return self._all_tools

    def get_all_tools_by_name(self):
        """Get all available MCP tools as a dictionary keyed by tool name.

        Usage: `tools_dict = mcp_service.get_all_tools_by_name()`
        """
        all_tools: Dict[str, StructuredTool] = {}
        tools = self._all_tools
        for tool in tools:
            all_tools[tool.name] = tool

        return all_tools
