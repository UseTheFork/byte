import sys
from typing import TYPE_CHECKING

from rich.traceback import Traceback

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class HandleExceptions(Bootstrapper):
    """Bootstrap exception handling for the application."""

    app: Application

    def _render_for_console(self, exception: Exception) -> None:
        """Render an exception for the console using Rich."""
        console = HandleExceptions.app["console"]

        traceback = Traceback.from_exception(
            type(exception),
            exception,
            exception.__traceback__,
            max_frames=20,
            show_locals=False,
        )
        console.print(traceback)

        # TODO: Check if in dev mode and vary exception printing based on that.
        # console.print_error_panel(f"{e}", title="Oops")

    def _render_for_logging(self, exception: Exception) -> None:
        """Render an exception for logging."""
        log = HandleExceptions.app["log"]

        log.exception(exception)

    def _make_exception_handler(self):
        """Create the exception handler callable."""

        def exception_handler(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions."""

            # Render for console
            self._render_for_console(exc_value)
            self._render_for_logging(exc_value)

        return exception_handler

    def bootstrap(self, app: Application) -> None:
        """Bootstrap exception handling."""

        HandleExceptions.app = app

        # Install exception handler
        sys.excepthook = self._make_exception_handler()
