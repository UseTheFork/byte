from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.traceback import Traceback

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class HandleExceptions(Bootstrapper):
    """Bootstrap exception handling for the application."""

    app: Application | None = None

    def _render_for_console(self, exception: Exception) -> None:
        """
        Render an exception for the console using Rich.

        Args:
            exception: The exception to render.
        """
        console = Console(stderr=True)

        traceback = Traceback.from_exception(
            type(exception),
            exception,
            exception.__traceback__,
            show_locals=True,
        )
        console.print(traceback)

    def _make_exception_handler(self):
        """
        Create the exception handler callable.

        Returns:
            Callable exception handler.
        """

        def exception_handler(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions."""

            # Render for console
            self._render_for_console(exc_value)

        return exception_handler

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap exception handling.

        Args:
            app: The application instance.
        """

        HandleExceptions.app = app

        # Install exception handler
        sys.excepthook = self._make_exception_handler()
