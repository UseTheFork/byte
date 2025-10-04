from rich.columns import Columns
from rich.panel import Panel

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.domain.knowledge.service.convention_context_service import (
    ConventionContextService,
)
from byte.domain.knowledge.service.session_context_service import SessionContextService


class CLIContextDisplayService(Service):
    async def display_context_panel_hook(self, payload: Payload) -> Payload:
        """Display session context and convention panels showing all active items."""

        info_panel = payload.get("info_panel", [])

        context_panel = None
        session_context_service = await self.make(SessionContextService)
        context_items = session_context_service.get_all_context()
        if context_items:
            context_names = [f"[text]{key}[/text]" for key in context_items.keys()]
            context_panel = Panel(
                Columns(context_names, equal=True, expand=True),
                title=f"[bold info]Session Context ({len(context_items)})[/bold info]",
                border_style="info",
            )

        if context_panel:
            info_panel.append(context_panel)

        convention_panel = None
        convention_context_service = await self.make(ConventionContextService)
        convention_items = convention_context_service.conventions.all()
        if convention_items:
            convention_names = [
                f"[text]{key}[/text]" for key in convention_items.keys()
            ]
            convention_panel = Panel(
                Columns(convention_names, equal=True, expand=True),
                title=f"[bold info]Conventions ({len(convention_items)})[/bold info]",
                border_style="info",
            )

        if convention_panel:
            info_panel.append(convention_panel)

        return payload.set("info_panel", info_panel)
