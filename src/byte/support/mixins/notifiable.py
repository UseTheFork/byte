from textual.notifications import SeverityLevel

from byte.support.mixins import Eventable
from byte.tui import Messages


class Notifiable(Eventable):
    """Mixin for displaying flash/toast notifications to users."""

    async def notify(
        self,
        message: str,
        style: SeverityLevel = "information",
        duration: float = 3,
    ) -> None:
        """Display a default notification."""

        self.emit_tui(
            Messages.Notify(
                content=message,
                style=style,
                duration=duration,
            )
        )

    async def notify_success(self, message: str, duration: float = 3) -> None:
        """Display a success notification (green)."""
        await self.notify(message, "information", duration)

    async def notify_warning(self, message: str, duration: float = 3) -> None:
        """Display a warning notification (yellow)."""
        await self.notify(message, "warning", duration)

    async def notify_error(self, message: str, duration: float = 3) -> None:
        """Display an error notification (red)."""
        await self.notify(message, "error", duration)
