from rich.table import Table

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.service.convention_context_service import (
    ConventionContextService,
)
from byte.domain.knowledge.service.session_context_service import SessionContextService


class CLIContextDisplayService(Service):
    async def display_context_panel_hook(self, payload: Payload) -> Payload:
        """Display session context and convention panels showing all active items."""

        console = await self.make(ConsoleService)
        info_panel = payload.get("info_panel", [])

        session_context_service = await self.make(SessionContextService)
        context_items = session_context_service.get_all_context()

        convention_context_service = await self.make(ConventionContextService)
        convention_items = convention_context_service.conventions.all()

        context_markdown = None
        convention_markdown = None

        context_markdown = "[secondary]Session Context[/secondary]\n" + "\n".join(
            f"{key}" for key in context_items.keys()
        )

        convention_markdown = "[secondary]Conventions[/secondary]\n" + "\n".join(
            f"{key}" for key in convention_items.keys()
        )

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(width=2)
        grid.add_column(ratio=1)
        grid.add_row(
            context_markdown,
            None,
            convention_markdown,
        )

        # Create panel with columns if there are any sections
        combined_panel = console.panel(
            grid,
            title="Knowledge Context",
        )
        info_panel.append(combined_panel)

        return payload.set("info_panel", info_panel)
