from typing import Literal

from byte.support.mixins import Eventable
from byte.tui import TuiComponentEvents, TuiEvents


class Notifiable(Eventable):
    """Mixin for displaying flash/toast notifications to users."""

    async def notify(
        self,
        message: str,
        style: Literal["default", "warning", "success", "error"] = "default",
        duration: float | None = None,
    ) -> None:
        """Display a default notification."""

        await self.emit(
            TuiEvents.ComponentEvent(
                TuiComponentEvents.Notify(
                    content=message,
                    style=style,
                    duration=duration,
                )
            )
        )

    async def notify_success(self, message: str, duration: float | None = None) -> None:
        """Display a success notification (green)."""
        await self.notify(message, "success", duration)

    async def notify_warning(self, message: str, duration: float | None = None) -> None:
        """Display a warning notification (yellow)."""
        await self.notify(message, "warning", duration)

    async def notify_error(self, message: str, duration: float | None = None) -> None:
        """Display an error notification (red)."""
        await self.notify(message, "error", duration)
