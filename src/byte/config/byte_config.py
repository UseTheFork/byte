from pathlib import Path
from typing import Optional

import git
from pydantic import BaseModel, Field

from byte.cli.config import CLIConfig
from byte.files.config import FilesConfig
from byte.git.config import GitConfig
from byte.lint.config import LintConfig
from byte.llm.config import LLMConfig
from byte.lsp.config import LSPConfig
from byte.presets.config import PresetsConfig
from byte.prompt_format.config import EditFormatConfig
from byte.system.config import SystemConfig
from byte.web.config import WebConfig


def _find_project_root() -> Path:
    """Find git repository root directory.

    Raises InvalidGitRepositoryError if not in a git repository.
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        return Path(repo.working_dir)
    except git.InvalidGitRepositoryError:
        raise git.InvalidGitRepositoryError(
            "Byte requires a git repository. Please run 'git init' or navigate to a git repository."
        )


# PROJECT_ROOT = _find_project_root()
# BYTE_DIR: Path = PROJECT_ROOT / ".byte"
# BYTE_DIR.mkdir(exist_ok=True)

# BYTE_CACHE_DIR: Path = BYTE_DIR / "cache"
# BYTE_CACHE_DIR.mkdir(exist_ok=True)

# BYTE_SESSION_DIR: Path = BYTE_DIR / "session_context"
# BYTE_SESSION_DIR.mkdir(exist_ok=True)

# BYTE_CONFIG_FILE = BYTE_DIR / "config.yaml"

# # Load our dotenv
# DOTENV_PATH = PROJECT_ROOT / ".env"


class CLIArgs(BaseModel):
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")


# TODO: should this be moved to a boot domain or to the syste, domain?
class BootConfig(BaseModel):
    read_only_files: list[str] = Field(default_factory=list, description="Files to add to read-only context")
    editable_files: list[str] = Field(default_factory=list, description="Files to add to editable context")


class AppConfig(BaseModel):
    env: str = Field(default="production", exclude=True, description="XXXX")


class ByteConfig(BaseModel):
    dotenv_loaded: bool = Field(default=False, exclude=True, description="Whether a .env file was successfully loaded")

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
