from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LSPServerConfig(BaseModel):
    """Configuration for a single LSP server."""

    command: List[str] = Field(
        description="Command and arguments to start the LSP server (e.g., ['typescript-language-server', '--stdio'])"
    )
    languages: List[str] = Field(
        description="List of language names this server handles (e.g., ['typescript', 'javascript']). Empty list means all files."
    )
    initialization_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional initialization options to pass to the LSP server"
    )


class LSPConfig(BaseModel):
    """LSP domain configuration with validation and defaults."""

    enable: bool = Field(default=False, description="Enable or disable LSP functionality")
    timeout: int = Field(default=30, description="Timeout in seconds for LSP requests")
    servers: Dict[str, LSPServerConfig] = Field(
        default_factory=dict, description="Map of server names to their configurations"
    )
