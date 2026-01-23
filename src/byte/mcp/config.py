from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MCPConnection(BaseModel):
    """Connection configuration for MCP servers."""

    transport: str = Field(description="Transport type: 'stdio' or 'streamable_http'")
    # For stdio transport
    command: Optional[str] = Field(default=None, description="Command to execute for stdio transport")
    args: Optional[List[str]] = Field(default=None, description="Arguments to pass to the command")
    # For streamable_http transport
    url: Optional[str] = Field(default=None, description="URL for HTTP transport connection")
    headers: Optional[Dict[str, str]] = Field(default=None, description="HTTP headers for the connection")


class AgentToolFilter(BaseModel):
    """Tool filtering configuration for specific agents."""

    include: Optional[List[str]] = Field(
        default=None,
        description="Tools to include (if specified, only these tools will be available)",
    )
    exclude: Optional[List[str]] = Field(default=None, description="Tools to exclude from this agent")


class ToolCommandFilter(BaseModel):
    """Tool filtering configuration for the /tool command."""

    include: Optional[List[str]] = Field(
        default=None,
        description="Tools to expose via /tool command (if specified, only these tools will be available)",
    )


class MCPServer(BaseModel):
    """MCP server configuration with connection and agent-specific tool filtering."""

    name: str
    connection: MCPConnection
    agents: Optional[Dict[str, AgentToolFilter]] = Field(
        default=None, description="Agent-specific tool filtering (e.g., 'ask', 'coder')"
    )
    tool_command: Optional[ToolCommandFilter] = Field(
        default=None,
        description="Tool filtering for /tool command - exposes MCP tools directly to user",
    )
