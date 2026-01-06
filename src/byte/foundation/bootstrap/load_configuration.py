from __future__ import annotations

from typing import TYPE_CHECKING

from byte import dd
from byte.config import ByteConfig
from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class LoadConfiguration(Bootstrapper):
    """Bootstrap class for loading configuration."""

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """

        config = app.instance("config", ByteConfig())
        self.load_configuration_file(app, config)

        # app.detect_environment(lambda: config.get("app.env", "production"))

        # app.resolve_environment_using(lambda environments: app.environment(*environments))

    def load_configuration_file(self, app: Application, config: ByteConfig) -> None:
        """
        Load the primary configuration file.

        Args:
            repository: The configuration repository.
            name: The configuration key name.
            path: The path to the configuration file.
        """
        # Load the configuration file
        dd(app.config_path("config.yaml"))
