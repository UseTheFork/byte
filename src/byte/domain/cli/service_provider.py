from byte.container import Container
from byte.core.config.config import ByteConfg
from byte.core.event_bus import EventBus, EventType, Payload
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.cli.service.interactions_service import InteractionService
from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService
from byte.domain.cli.service.stream_rendering_service import (
    StreamRenderingService,
)
from byte.domain.cli.service.subprocess_service import SubprocessService


class CLIServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self):
        return [
            StreamRenderingService,
            InteractionService,
            PromptToolkitService,
            SubprocessService,
        ]

    async def boot(self, container: Container):
        """Boot UI services."""
        event_bus = await container.make(EventBus)

        event_bus.on(
            EventType.POST_BOOT.value,
            self.boot_messages,
        )

    async def boot_messages(self, payload: Payload) -> Payload:
        container: Container = payload.get("container", False)
        if container:
            config = await container.make(ByteConfg)
            console = await container.make(ConsoleService)
            messages = payload.get("messages", [])

            # Create diagonal gradient from primary to secondary color
            logo_lines = [
                "░       ░░░  ░░░░  ░░        ░░        ░",
                "▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒",
                "▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓",
                "█  ████  █████  ████████  █████  ███████",
                "█       ██████  ████████  █████        █",
            ]

            for row_idx, line in enumerate(logo_lines):
                styled_line = ""
                for col_idx, char in enumerate(line):
                    # Calculate diagonal position (0.0 = top-left, 1.0 = bottom-right)
                    diagonal_progress = (row_idx + col_idx) / (len(logo_lines) + len(line) - 2)

                    # Use primary for first half, secondary for second half of diagonal
                    if diagonal_progress < 0.5:
                        styled_line += f"[primary]{char}[/primary]"
                    else:
                        styled_line += f"[secondary]{char}[/secondary]"

                # Fill remaining width with the last character
                logo_width = len(line)
                remaining_width = console.width - logo_width - 4

                if remaining_width > 0:
                    last_char = line[-1] if line else " "
                    last_diagonal_progress = (row_idx + len(line) - 1) / (len(logo_lines) + len(line) - 2)
                    style = "primary" if last_diagonal_progress < 0.5 else "secondary"
                    styled_line += f"[{style}]{last_char * remaining_width}[/{style}]"

                messages.append(styled_line)

            # Add a break betwean the logo and the rest of the content
            messages.append("")

            messages.append(f"[muted]Version:[/muted] [primary]{config.system.version}[/primary]")

            if config.dotenv_loaded:
                messages.append(f"[muted]Env File Found:[/muted] [primary]{config.dotenv_loaded}[/primary]")

            messages.append(f"[muted]Project Root:[/muted] [primary]{config.project_root}[/primary]")

            payload.set("messages", messages)

        return payload
