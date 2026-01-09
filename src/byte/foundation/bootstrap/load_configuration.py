from __future__ import annotations

import os
from typing import TYPE_CHECKING

import yaml

from byte.config import ByteConfig
from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class LoadConfiguration(Bootstrapper):
    """Bootstrap class for loading configuration."""

    def _load_configuration_file(self, app: Application) -> dict:
        """
        Load the primary configuration file.

        Args:
            repository: The configuration repository.
            name: The configuration key name.
            path: The path to the configuration file.
        """
        # Load the configuration file
        config_file_path = app.config_path("config.yaml")
        if config_file_path.exists():
            with open(config_file_path) as f:
                config = yaml.safe_load(f)

        return config if config is not None else {}

    def _load_llm_api_keys(self, app: Application, config: ByteConfig):
        """Load and configure LLM API keys from environment variables.

        Detects available API keys and enables corresponding LLM providers.
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

    def _load_boot_config(self, app: Application, config: ByteConfig):
        """Load boot configuration from CLI arguments.

        Merges boot config from YAML with CLI arguments, removing duplicates.
        Usage: `config = self._load_boot_config(config)`
        """

        args = app["args"]
        read_only_files = args.get("options", {}).get("read_only", [])
        editable_files = args.get("options", {}).get("editable", [])

        # Merge read_only_files from YAML and CLI, removing duplicates
        read_only_files = list(set(config.boot.read_only_files + read_only_files))
        config.boot.read_only_files = read_only_files

        # Merge editable_files from YAML and CLI, removing duplicates
        editable_files = list(set(config.boot.editable_files + editable_files))
        config.boot.editable_files = editable_files

    def _setup_console(self, app: Application, config: ByteConfig):
        """Configure console UI and syntax themes from configuration.

        Usage: `self._setup_console(app, config)`
        """
        console = app["console"]
        console.ui_theme = config.cli.ui_theme
        console.syntax_theme = config.cli.syntax_theme
        console.setup_console()

    def _setup_environment(self, app: Application, config: ByteConfig):
        """Configure application environment settings including debug mode.

        Usage: `self._setup_environment(app, config)`
        """
        args = app["args"]

        flags = args.get("flags", [])
        byte_debug = os.getenv("BYTE_DEBUG", "").lower() in ("true", "1", "yes")

        if "debug" in flags or byte_debug:
            config.app.debug = True

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """

        yaml_config = self._load_configuration_file(app)
        config = app.instance("config", ByteConfig(**yaml_config))
        self._setup_console(app, config)
        self._setup_environment(app, config)
        self._load_llm_api_keys(app, config)
        self._load_boot_config(app, config)

        app.detect_environment(lambda: config.app.env)
        # app.resolve_environment_using(lambda environments: app.environment(*environments))
