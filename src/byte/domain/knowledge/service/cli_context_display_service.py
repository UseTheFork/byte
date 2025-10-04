from rich.columns import Columns
from rich.markdown import Markdown
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

        session_context_service = await self.make(SessionContextService)
        context_items = session_context_service.get_all_context()

        convention_context_service = await self.make(ConventionContextService)
        convention_items = convention_context_service.conventions.all()

        # Build list of markdown sections to include
        sections = []

        if context_items:
            context_markdown = "**Session Context**\n" + "\n".join(
                f"- {key}" for key in context_items.keys()
            )
            sections.append(Markdown(context_markdown, justify="left"))

        if convention_items:
            convention_markdown = "**Conventions**\n" + "\n".join(
                f"- {key}" for key in convention_items.keys()
            )
            sections.append(Markdown(convention_markdown, justify="left"))

        # Create panel with columns if there are any sections
        if sections:
            combined_panel = Panel(
                Columns(sections, equal=True, expand=True),
                title="Knowledge Context",
                border_style="info",
            )
            info_panel.append(combined_panel)

        return payload.set("info_panel", info_panel)
