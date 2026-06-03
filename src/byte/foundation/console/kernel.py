from __future__ import annotations

from typing import TYPE_CHECKING

from byte.foundation.bootstrap import (
    HandleExceptions,
    LoadConfiguration,
    LoadConsoleArgs,
    LoadEnvironmentVariables,
    PrepareEnvironment,
    RegisterProviders,
)

if TYPE_CHECKING:
    from byte.foundation import Application


class Kernel:
    """Kernel for"""

    def __init__(self, app: Application, **kwargs):
        self.app = app

    def bootstrappers(self):
        return [
            LoadEnvironmentVariables,
            LoadConsoleArgs,
            PrepareEnvironment,
            LoadConfiguration,
            HandleExceptions,
            RegisterProviders,
            # BootProviders,
        ]

    def bootstrap(self) -> None:
        """
        Bootstrap the application for artisan commands.

        Returns:
            None
        """
        if not self.app.has_been_bootstrapped():
            self.app.bootstrap_with(self.bootstrappers())

            # if not self.commands_loaded:
            #     # Auto-discover commands from app/commands/ directory
            #     if self.app.base_path:
            #         commands_dir = self.app.path("console/commands")
            #         if commands_dir.exists() and commands_dir.is_dir():
            #             self._discover_commands_from_directory(commands_dir)

            # if self.should_discover_commands():
            #     self.discover_commands()

    async def handle(self, input: list[str]) -> int:
        """
        Handle an incoming console command.

        Returns:
            Exit status code.
        """
        self.bootstrap()

        # Now we can Async boot all the providers
        await self.app.boot()

        return await self.app.run()

    def terminate(self):
        self.app.terminate()
        # TODO: this.
        # self.events.dispatch(Terminating())
