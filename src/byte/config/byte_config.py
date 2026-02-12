from typing import Optional

from pydantic import BaseModel, Field

from byte.cli.config import CLIConfig
from byte.code_operations.config import EditFormatConfig
from byte.files.config import FilesConfig
from byte.git.config import GitConfig
from byte.lint.config import LintConfig
from byte.llm.config import LLMConfig
from byte.lsp.config import LSPConfig
from byte.presets.config import PresetsConfig
from byte.system.config import SystemConfig
from byte.web.config import WebConfig


class CLIArgs(BaseModel):
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")


# TODO: should this be moved to a boot domain or to the syste, domain?
class BootConfig(BaseModel):
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")


class AppConfig(BaseModel):
    env: str = Field(default="production", exclude=True, description="XXXX")
    debug: bool = Field(default=False, exclude=True, description="XXXX")
    version: str = Field(default="0.0.0", exclude=True, description="XXXX")


class ByteConfig(BaseModel):
    version: str = Field(default="0.0.0", exclude=True, description="XXXX")

    # keep-sorted start
    app: AppConfig = Field(default_factory=AppConfig)
    boot: BootConfig = Field(default_factory=BootConfig)
    cli: CLIConfig = Field(default_factory=CLIConfig)
    edit_format: EditFormatConfig = Field(default_factory=EditFormatConfig)
    files: FilesConfig = Field(default_factory=FilesConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    lint: LintConfig = Field(default_factory=LintConfig, description="Code linting and formatting configuration")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    lsp: LSPConfig = Field(default_factory=LSPConfig)
    presets: Optional[list[PresetsConfig]] = Field(default_factory=list)
    system: SystemConfig = Field(default_factory=SystemConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    # keep-sorted end
