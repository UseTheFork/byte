from typing import Optional

from pydantic import BaseModel, Field

from byte.documentation.config import DocumentationConfig
from byte.files.config import FilesConfig
from byte.gateway.config import GatewayConfig
from byte.git.config import GitConfig
from byte.lint.config import LintConfig
from byte.llm.config import LLMConfig
from byte.presets.config import PresetsConfig
from byte.tui.config import TUIConfig
from byte.web.config import WebConfig


# TODO: should this be moved to a boot domain or to the system domain?
class BootConfig(BaseModel):
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")


class AppConfig(BaseModel):
    env: str = Field(default="production")
    debug: bool = Field(default=False)
    version: str = Field(default="0.0.0")


class ByteUserConfig(BaseModel):
    # keep-sorted start

    documentation: DocumentationConfig = Field(
        default_factory=DocumentationConfig,
        description="Documentation framework, features, and writing style configuration",
    )
    files: FilesConfig = Field(
        default_factory=FilesConfig, description="File discovery, watching, and ignore pattern configuration"
    )
    gateway: GatewayConfig = Field(
        default_factory=GatewayConfig, description="WebSocket JSON-RPC 2.0 gateway server configuration"
    )
    git: GitConfig = Field(
        default_factory=GitConfig, description="Git operations and conventional commit behavior configuration"
    )
    lint: LintConfig = Field(default_factory=LintConfig, description="Code linting and formatting configuration")
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM provider and model assignment configuration")
    # lsp: LSPConfig = Field(default_factory=LSPConfig)
    presets: Optional[list[PresetsConfig]] = Field(
        default_factory=list, description="Predefined context and prompt presets"
    )
    tui: TUIConfig = Field(
        default_factory=TUIConfig, description="Terminal UI theme and syntax highlighting configuration"
    )
    web: WebConfig = Field(default_factory=WebConfig, description="Web browser automation and scraping configuration")
    # keep-sorted end


class ByteConfig(ByteUserConfig):
    version: str = Field(default="0.0.0")

    # keep-sorted start
    app: AppConfig = Field(default_factory=AppConfig)
    boot: BootConfig = Field(default_factory=BootConfig)
    # keep-sorted end
