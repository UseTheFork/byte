import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from byte.config import ByteConfig
from byte.foundation.bootstrap.bootstrapper import Bootstrapper
from byte.support import Json

if TYPE_CHECKING:
    from byte.foundation import Application


class LoadConfiguration(Bootstrapper):
    """Bootstrap class for loading configuration."""

    @staticmethod
    def _find_binary(binary_names: list[str]) -> Path | None:
        """Search for a binary in common filesystem locations.

        Args:
            binary_names: List of binary names to search for.

        Returns:
            Path to the first found binary, or None if no binary is found.
        """
        common_paths = [Path("/usr/bin"), Path("/usr/local/bin"), Path("/opt/homebrew/bin")]

        for binary_name in binary_names:
            # First try shutil.which for system PATH search
            which_result = shutil.which(binary_name)
            if which_result:
                return Path(which_result)

            # Then check common paths
            for common_path in common_paths:
                binary_path = common_path / binary_name
                if binary_path.exists():
                    return binary_path

        return None

    def _load_configuration_file(self, app: Application) -> dict:
        """
        Load the primary configuration file.

        Args:
            repository: The configuration repository.
            name: The configuration key name.
            path: The path to the configuration file.
        """

        config_file_path = app.config_path("config.jsonc")
        return Json.load_as_dict(config_file_path)

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

    def _configure_web_browser(self, config: ByteConfig) -> None:
        """Auto-detect and configure Chrome/Chromium binary.

        Searches for Chrome/Chromium binary if web config is not explicitly enabled,
        and updates the config with the detected binary location.

        Args:
            config: The ByteConfig instance to update.
        """
        if not config.web.enable:
            chrome_binary = self._find_binary(["google-chrome-stable", "chromium"])
            if chrome_binary:
                config.web.enable = True
                config.web.chrome_binary_location = chrome_binary

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """

        user_config = self._load_configuration_file(app)

        config = app.instance("config", ByteConfig(**user_config))
        self._load_boot_config(app, config)
        self._configure_web_browser(config)

        app.detect_environment(lambda: config.app.env)
        # app.resolve_environment_using(lambda environments: app.environment(*environments))
