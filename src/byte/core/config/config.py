from pathlib import Path

import git
from pydantic import BaseModel, Field

from byte.domain.cli.config import CLIConfig
from byte.domain.development.config import DevelopmentConfig
from byte.domain.edit_format.config import EditFormatConfig
from byte.domain.files.config import FilesConfig
from byte.domain.lint.config import LintConfig
from byte.domain.llm.config import LLMConfig
from byte.domain.lsp.config import LSPConfig
from byte.domain.web.config import WebConfig


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


PROJECT_ROOT = _find_project_root()
BYTE_DIR: Path = PROJECT_ROOT / ".byte"
BYTE_DIR.mkdir(exist_ok=True)

BYTE_CACHE_DIR: Path = BYTE_DIR / "cache"
BYTE_CACHE_DIR.mkdir(exist_ok=True)

BYTE_CONFIG_FILE = BYTE_DIR / "config.yaml"

# Load our dotenv
DOTENV_PATH = PROJECT_ROOT / ".env"


class ByteConfg(BaseModel):
	project_root: Path = Field(default=PROJECT_ROOT, exclude=True)
	byte_dir: Path = Field(default=BYTE_DIR, exclude=True)
	byte_cache_dir: Path = Field(default=BYTE_CACHE_DIR, exclude=True)
	dotenv_loaded: bool = Field(default=False, exclude=True, description="Whether a .env file was successfully loaded")

	# keep-sorted start
	cli: CLIConfig = CLIConfig()
	development: DevelopmentConfig = Field(default_factory=DevelopmentConfig, exclude=True)
	edit_format: EditFormatConfig = EditFormatConfig()
	files: FilesConfig = FilesConfig()
	lint: LintConfig = LintConfig()
	llm: LLMConfig = LLMConfig()
	lsp: LSPConfig = LSPConfig()
	web: WebConfig = WebConfig()
	# keep-sorted end
