import os
import shutil
from importlib.metadata import PackageNotFoundError, version

import yaml

from byte.core.config.config import BYTE_CONFIG_FILE, ByteConfg, CLIArgs
from byte.domain.system.config import PathsConfig


class ConfigLoaderService:
    """Load and parse configuration from YAML file.

    Loads the BYTE_CONFIG_FILE and returns a dictionary that can be
    passed to ByteConfig for initialization.
    Usage: `loader = ConfigLoaderService(cli_args)`
    Usage: `config_dict = loader()` -> {"llm": {...}, "files": {...}}
    """

    def __init__(self, cli_args: CLIArgs | None = None):
        self.cli_args = cli_args or CLIArgs()

    def _load_yaml_config(self) -> dict:
        """Load and parse YAML configuration file.

        Returns a dictionary of configuration values from YAML file.
        Usage: `config_dict = self._load_yaml_config()`
        """
        with open(BYTE_CONFIG_FILE) as f:
            config = yaml.safe_load(f)

        return config if config is not None else {}

    def _apply_system_config(self, config: ByteConfg) -> ByteConfg:
        """Apply system-level configuration settings.

        Usage: `config = self._apply_system_config(config)`
        """

        try:
            config.system.version = version("byte-ai-cli")
        except PackageNotFoundError:
            pass

        config.system.paths = PathsConfig(
            cache=config.byte_dir / "cache",
            session_context=config.byte_dir / "session_context",
            conventions=config.byte_dir / "conventions",
        )

        # Create the directories

        # Delete and recreate session_context to ensure it's empty on each boot
        if config.system.paths.session_context.exists():
            shutil.rmtree(config.system.paths.session_context)
        config.system.paths.session_context.mkdir(exist_ok=True)

        config.system.paths.cache.mkdir(exist_ok=True)
        config.system.paths.conventions.mkdir(exist_ok=True)

        return config

    def _apply_environment_overrides(self, config: ByteConfg) -> ByteConfg:
        """Apply environment variable overrides to configuration.

        Checks for BYTE_DEV_MODE environment variable and enables development mode if set.
        Usage: `config = self._apply_environment_overrides(config)`
        """
        # Enable development mode if BYTE_DEV_MODE environment variable is set
        if os.getenv("BYTE_DEV_MODE", "").lower() in ("true", "1", "yes"):
            config.development.enable = True

        return config

    def _load_llm_api_keys(self, config: ByteConfg) -> ByteConfg:
        """Load and configure LLM API keys from environment variables.

        Detects available API keys and enables corresponding LLM providers.
        Validates that at least one provider is configured.
        Usage: `config = self._load_llm_api_keys(config)`
        """
        # Auto-detect and configure Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            config.llm.anthropic.enable = True
            config.llm.anthropic.api_key = anthropic_key

        # Auto-detect and configure Anthropic
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            config.llm.gemini.enable = True
            config.llm.gemini.api_key = gemini_key

        # Auto-detect and configure OpenAI
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            config.llm.openai.enable = True
            config.llm.openai.api_key = openai_key

        # Validate that at least one provider is configured
        if not (config.llm.anthropic.enable or config.llm.gemini.enable or config.llm.openai.enable):
            raise ValueError(
                "Missing required API key. Please set at least one of: "
                "ANTHROPIC_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY environment variable."
            )

        return config

    def _load_boot_config(self, config: ByteConfg) -> ByteConfg:
        """Load boot configuration from CLI arguments.

        Merges boot config from YAML with CLI arguments, removing duplicates.
        Usage: `config = self._load_boot_config(config)`
        """

        # Merge read_only_files from YAML and CLI, removing duplicates
        read_only_files = list(set(config.boot.read_only_files + self.cli_args.read_only_files))
        config.boot.read_only_files = read_only_files

        # Merge editable_files from YAML and CLI, removing duplicates
        editable_files = list(set(config.boot.editable_files + self.cli_args.editable_files))
        config.boot.editable_files = editable_files

        return config

    def __call__(self) -> ByteConfg:
        """Load configuration from BYTE_CONFIG_FILE.

        Returns a dictionary of configuration values parsed from YAML.
        Usage: `config_dict = loader()`
        """

        yaml_config = self._load_yaml_config()

        config = ByteConfg(**yaml_config)
        config = self._apply_system_config(config)
        config = self._apply_environment_overrides(config)
        config = self._load_llm_api_keys(config)
        config = self._load_boot_config(config)

        return config
