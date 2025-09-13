import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from byte.core.config.schema import Config


class ConfigService:
    """Configuration service with automatic workspace initialization.

    Manages configuration in a .byte directory within the project root,
    creating default configurations and directory structure as needed.
    Usage: `config.get('app.name')` -> automatically initializes workspace
    """

    def __init__(
        self, config_data: Optional[Dict] = None, cli_args: Optional[Dict] = None
    ):
        self._raw_config: Dict[str, Any] = config_data or {}
        self._cli_args: Dict[str, Any] = cli_args or {}
        self._typed_config: Optional[Config] = None
        self._loaded_files: set = set()
        self._project_root: Optional[Path] = None
        self._byte_dir: Optional[Path] = None

        # Initialize workspace on creation
        self._initialize_workspace()

    def _initialize_workspace(self) -> None:
        """Initialize .byte workspace directory and load configurations."""
        self._project_root = self._find_project_root()
        self._byte_dir = self._project_root / ".byte"

        # Only ensure .byte directory exists - don't create config files
        self._byte_dir.mkdir(exist_ok=True)

        # Load config.yaml if it exists
        config_file = self._byte_dir / "config.yaml"
        if config_file.exists():
            self.load_yaml(str(config_file))

        # Load environment variables
        self._load_env_config()

        # Apply CLI arguments (highest priority)
        self._apply_cli_args()

        # Detect git repository
        has_git = (self._project_root / ".git").exists()

        # Create typed config with computed values and all sources merged
        self._typed_config = Config.from_dict(
            self._raw_config, self._project_root, has_git
        )

    def _find_project_root(self) -> Path:
        """Find project root by looking for .git directory or using current directory."""
        current = Path.cwd()

        # Walk up directory tree looking for .git
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent

        # Fall back to current directory if no git repo found
        return current

    def _load_env_config(self) -> None:
        """Load configuration from environment variables with BYTE_ prefix."""
        env_config = {}

        # Map environment variables to config structure
        env_mappings = {
            "BYTE_DEBUG": ("app", "debug", lambda x: x.lower() == "true"),
            "BYTE_LLM_PROVIDER": ("llm", "provider", str),
            "BYTE_LLM_MODEL": ("llm", "model", str),
            "BYTE_LLM_TEMPERATURE": ("llm", "temperature", float),
            "BYTE_THEME": ("ui", "theme", str),
            "BYTE_CODE_THEME": ("code-theme", None, str),  # Top-level key
            "BYTE_DARK_MODE": ("dark-mode", None, lambda x: x.lower() == "true"),
            "BYTE_AUTO_COMMITS": ("auto-commits", None, lambda x: x.lower() == "true"),
        }

        for env_var, (section, key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = converter(value)
                    if key is None:
                        # Top-level key
                        env_config[section] = converted_value
                    else:
                        # Nested key
                        if section not in env_config:
                            env_config[section] = {}
                        env_config[section][key] = converted_value
                except (ValueError, TypeError) as e:
                    print(f"Invalid environment variable {env_var}={value}: {e}")

        # Merge environment config
        if env_config:
            self._merge_config(env_config)

    def _apply_cli_args(self) -> None:
        """Apply CLI arguments as highest priority config overrides."""
        if not self._cli_args:
            return

        # Map CLI args to config structure
        cli_config = {}

        # Example CLI arg mappings
        cli_mappings = {
            "debug": ("app", "debug"),
            "provider": ("llm", "provider"),
            "model": ("llm", "model"),
            "temperature": ("llm", "temperature"),
            "theme": ("ui", "theme"),
            "code_theme": ("code-theme", None),  # Top-level
            "dark_mode": ("dark-mode", None),
            "auto_commits": ("auto-commits", None),
        }

        for cli_key, (section, config_key) in cli_mappings.items():
            if cli_key in self._cli_args:
                value = self._cli_args[cli_key]
                if config_key is None:
                    # Top-level key
                    cli_config[section] = value
                else:
                    # Nested key
                    if section not in cli_config:
                        cli_config[section] = {}
                    cli_config[section][config_key] = value

        # Merge CLI config (highest priority)
        if cli_config:
            self._merge_config(cli_config)

    @property
    def project_root(self) -> Path:
        """Get the detected project root directory."""
        if self._project_root is None:
            raise RuntimeError("Project root not initialized")
        return self._project_root

    @property
    def byte_dir(self) -> Path:
        """Get the .byte workspace directory."""
        if self._byte_dir is None:
            raise RuntimeError("Byte directory not initialized")
        return self._byte_dir

    def get_cache_dir(self) -> Path:
        """Get cache directory, creating if needed."""
        if self._byte_dir is None:
            raise RuntimeError("Byte directory not initialized")
        cache_dir = self._byte_dir / "cache"
        cache_dir.mkdir(exist_ok=True)
        return cache_dir

    def get_logs_dir(self) -> Path:
        """Get logs directory, creating if needed."""
        if self._byte_dir is None:
            raise RuntimeError("Byte directory not initialized")
        logs_dir = self._byte_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def load_yaml(self, file_path: str) -> None:
        """Load configuration from YAML file.

        Usage: `config.load_yaml('.byte/config.yaml')` -> loads config into service
        """
        path = Path(file_path)
        if not path.exists():
            return

        if str(path) in self._loaded_files:
            return

        try:
            with open(path, encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
                self._merge_config(yaml_data)
                self._loaded_files.add(str(path))
                # Recreate typed config after loading new data
                if self._project_root:
                    has_git = (self._project_root / ".git").exists()
                    self._typed_config = Config.from_dict(
                        self._raw_config, self._project_root, has_git
                    )
        except (OSError, yaml.YAMLError) as e:
            print(f"Failed to load config from {file_path}: {e}")

    @property
    def config(self) -> Config:
        """Get strongly-typed configuration object.

        Usage: `config_service.config.app.name` -> type-safe access
        """
        if self._typed_config is None:
            project_root = self._project_root or Path.cwd()
            has_git = (project_root / ".git").exists() if project_root else False
            self._typed_config = Config.from_dict(
                self._raw_config, project_root, has_git
            )
        return self._typed_config

    def reload(self) -> None:
        """Reload configuration from disk and recreate typed config."""
        self._loaded_files.clear()
        self._raw_config.clear()
        if self._byte_dir:
            config_file = self._byte_dir / "config.yaml"
            if config_file.exists():
                self.load_yaml(str(config_file))
            if self._project_root:
                has_git = (self._project_root / ".git").exists()
                self._typed_config = Config.from_dict(
                    self._raw_config, self._project_root, has_git
                )

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Recursively merge new configuration into existing config."""

        def merge_dict(target: Dict, source: Dict):
            for key, value in source.items():
                if (
                    key in target
                    and isinstance(target[key], dict)
                    and isinstance(value, dict)
                ):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(self._raw_config, new_config)
