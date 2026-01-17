from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class LocalServerConfig(BaseModel):
    """Configuration for a local LSP server."""

    type: Literal["local"] = "local"
    program: str = Field(description="Program name or path to execute")
    args: List[str] = Field(default_factory=list, description="Command line arguments")


class ContainerServerConfig(BaseModel):
    """Configuration for a containerized LSP server."""

    type: Literal["container"] = "container"
    image: str = Field(description="Docker image name (e.g., 'ghcr.io/lsp-client/pyright:latest')")
    workspace_mount: Optional[str] = Field(default=None, description="Custom workspace mount path in container")


class PresetServerConfig(BaseModel):
    """Configuration using a prebuilt client from lsp-client."""

    preset: Literal["pyright", "basedpyright", "pyrefly", "ty", "rust_analyzer", "deno", "typescript", "gopls"] = Field(
        description="Name of the prebuilt LSP client"
    )
    server_type: Literal["local", "container"] = Field(
        default="container", description="Whether to use local or container server (if both available)"
    )
    initialization_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom initialization options to override defaults"
    )


class CustomServerConfig(BaseModel):
    """Configuration for a custom LSP server."""

    server: Union[LocalServerConfig, ContainerServerConfig] = Field(
        description="Server configuration (local or container)"
    )
    languages: List[str] = Field(description="List of language names this server handles")
    initialization_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Initialization options to pass to the LSP server"
    )


class LSPConfig(BaseModel):
    """LSP domain configuration with validation and defaults."""

    enable: bool = Field(default=False, description="Enable or disable LSP functionality")
    timeout: int = Field(default=30, description="Timeout in seconds for LSP requests")
    servers: Dict[str, Union[PresetServerConfig, CustomServerConfig]] = Field(
        default_factory=dict, description="Map of server names to their configurations"
    )
