from pathlib import Path
from typing import List

import git
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import (
	BaseSettings,
	PydanticBaseSettingsSource,
	SettingsConfigDict,
	YamlConfigSettingsSource,
)

from byte.domain.cli.config import CLIConfig
from byte.domain.edit_format.config import EditFormatConfig
from byte.domain.files.config import FilesConfig
from byte.domain.lint.config import LintConfig
from byte.domain.llm.config import LLMConfig
from byte.domain.mcp.config import MCPServer
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

BYTE_CACHE_DIR: Path = BYTE_DIR / "cache"
BYTE_CACHE_DIR.mkdir(exist_ok=True)

BYTE_CONFIG_FILE = BYTE_DIR / "config.yaml"

# Load our dotenv
DOTENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(DOTENV_PATH)


class ByteConfg(BaseSettings):
	model_config = SettingsConfigDict(
		env_nested_delimiter="_",
		env_nested_max_split=1,
		env_prefix="BYTE_",
		yaml_file=BYTE_CONFIG_FILE,
	)

	project_root: Path = Field(default=PROJECT_ROOT, exclude=True)
	byte_dir: Path = Field(default=BYTE_DIR, exclude=True)
	byte_cache_dir: Path = Field(default=BYTE_CACHE_DIR, exclude=True)

	cli: CLIConfig = CLIConfig()
	llm: LLMConfig = LLMConfig()
	lint: LintConfig = LintConfig()
	files: FilesConfig = FilesConfig()
	edit_format: EditFormatConfig = EditFormatConfig()
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
