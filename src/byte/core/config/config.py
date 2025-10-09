import os
from pathlib import Path
from typing import List

import git
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from byte.core.logging import log
from byte.domain.edit_format.config import EditFormatConfig
from byte.domain.files.config import FilesConfig
from byte.domain.lint.config import LintConfig
from byte.domain.mcp.config import MCPServer
from byte.domain.memory.config import MemoryConfig
from byte.domain.web.config import WebConfig


def _find_project_root() -> Path:
    """Find git repository root directory.

    Raises InvalidGitRepositoryError if not in a git repository.
    """
    try:
        # Use git library to find repository root
        repo = git.Repo(search_parent_directories=True)
        return Path(repo.working_dir)
    except git.InvalidGitRepositoryError:
        raise git.InvalidGitRepositoryError(
            "Byte requires a git repository. Please run 'git init' or navigate to a git repository."
        )


PROJECT_ROOT = _find_project_root()
BYTE_DIR: Path = PROJECT_ROOT / ".byte"
BYTE_DIR.mkdir(exist_ok=True)

BYTE_CONFIG_FILE = BYTE_DIR / "config.yaml"

# Load our dotenv
DOTENV_PATH = PROJECT_ROOT / ".env"

if not load_dotenv(DOTENV_PATH):
    log.warning(f"No .env file found at {DOTENV_PATH}")


def validate_api_keys() -> None:
    """Validate that at least one required API key is present in environment.

    Checks for ANTHROPIC_API_KEY or GEMINI_API_KEY environment variables.
    Raises ValueError if neither key is found.

    Usage: `validate_api_keys()`
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not anthropic_key and not gemini_key:
        raise ValueError(
            "Missing required API key. Please set either ANTHROPIC_API_KEY or GEMINI_API_KEY environment variable."
        )


class LLMProviderConfig(BaseModel):
    """Configuration for a specific LLM provider."""

    enabled: bool = False
    api_key: str = ""


class LLMConfig(BaseModel):
    """LLM domain configuration with provider-specific settings."""

    gemini: LLMProviderConfig = LLMProviderConfig()
    anthropic: LLMProviderConfig = LLMProviderConfig()
    openai: LLMProviderConfig = LLMProviderConfig()

    def __init__(self, **data):
        """Initialize LLM config with automatic API key detection from environment.

        Usage: `llm_config = LLMConfig()`
        """
        super().__init__(**data)

        # Auto-detect and configure Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            self.anthropic = LLMProviderConfig(enabled=True, api_key=anthropic_key)

        # Auto-detect and configure Gemini
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            self.gemini = LLMProviderConfig(enabled=True, api_key=gemini_key)

        # Auto-detect and configure OpenAI
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            self.openai = LLMProviderConfig(enabled=True, api_key=openai_key)

        # Validate that at least one provider is configured
        if not (self.anthropic.enabled or self.gemini.enabled or self.openai.enabled):
            raise ValueError(
                "Missing required API key. Please set at least one of: "
                "ANTHROPIC_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY environment variable."
            )


class ByteConfg(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_nested_max_split=1,
        env_prefix="BYTE_",
        yaml_file=BYTE_CONFIG_FILE,
    )

    project_root: Path = PROJECT_ROOT
    byte_dir: Path = BYTE_DIR

    model: str

    llm: LLMConfig = LLMConfig()
    lint: LintConfig = LintConfig()
    files: FilesConfig = FilesConfig()
    edit_format: EditFormatConfig = EditFormatConfig()
    memory: MemoryConfig = MemoryConfig()
    web: WebConfig = WebConfig()
    mcp: List[MCPServer] = []

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


class BaseConfig(BaseModel):
    pass
