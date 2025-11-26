from argparse import Namespace
from typing import TYPE_CHECKING, Any, Dict, List

from langchain_core.tools import StructuredTool

from byte.core.utils import dd, dump
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.mcp.service.mcp_service import MCPService

if TYPE_CHECKING:
    from byte.container import Container


# TODO: This needs to be finished.
class MCPToolCommand(Command):
    """Execute MCP tools directly via /tool command.

    Provides direct access to MCP tools based on tool_command configuration.
    Tools must be explicitly included in each server's tool_command.include list.
    Usage: `/tool read_file path=/path/to/file`
    """

    def __init__(self, container: "Container"):
        super().__init__(container)
        self._available_tools: Dict[str, Any] = {}

    async def boot(self):
        """Load and filter available tools based on configuration."""
        await self._refresh_available_tools()

    @property
    def name(self) -> str:
        return "tool"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Execute MCP tools directly.",
        )
        return parser

    # TODO: "Usage: /tool <tool_name> <args>"

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute an MCP tool with provided arguments.

        Usage: `/tool read_file path=/path/to/file timeout=30`
        """
        parts = args.strip().split(" ", 1)
        if not parts or not parts[0]:
            # Show available tools
            return

        tool_name = parts[0]
        tool: StructuredTool = self._available_tools.get(tool_name)  # pyright: ignore[reportAssignmentType]

        if not tool:
            # Handle unknown tool
            return

        tool_args = {}

        if hasattr(tool, "args_schema") or tool.args_schema:
            # Extract parameter names from tool's args_schema
            properties = tool.args_schema.get("properties", {})
            required = tool.args_schema.get("required", [])

            for param_name in properties.keys():
                message = param_name
                if param_name in required:
                    message = f"{message} (required)"

                input_result = await self.prompt_for_input(f"{message}:")

                tool_args[param_name] = input_result

        result = await tool.ainvoke(tool_args)

        dump(result)
        dd(tool_args)
        # # Parse key=value arguments
        # tool_args = {}
        # if len(parts) > 1:
        #     tool_args = self._parse_arguments(parts[1], tool.args_schema)

    async def get_completions(self, text: str) -> List[str]:
        """Return tab completion suggestions for available tool names.

        Usage: `/tool read` -> lists tool names starting with "read"
        """
        prefix = text.strip()
        return [tool_name for tool_name in self._available_tools.keys() if tool_name.startswith(prefix)]

    async def _refresh_available_tools(self):
        """Refresh the list of available tools from MCP service based on config."""
        # Get MCP service from container
        mcp_service = await self.make(MCPService)
        if not mcp_service:
            self._available_tools = {}
            return

        # Get all tools
        all_tools = mcp_service.get_all_tools_by_name()

        # Filter based on tool_command configuration
        filtered_tools: Dict[str, Any] = {}
        config_service = self._config
        if config_service and config_service.mcp:
            for server in config_service.mcp:
                if server.tool_command and server.tool_command.include:
                    # Only include explicitly listed tools from this server
                    for tool_name in server.tool_command.include:
                        if tool_name in all_tools:
                            filtered_tools[tool_name] = all_tools[tool_name]

        # If no tool_command filters defined anywhere, no tools are available
        self._available_tools = filtered_tools
