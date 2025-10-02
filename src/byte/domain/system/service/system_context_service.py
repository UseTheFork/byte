from datetime import datetime
from textwrap import dedent

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service


class SystemContextService(Service):
    """Service for injecting system-level context into agent prompts.

    Provides current system information like dates and environment context
    that helps the AI agent maintain temporal awareness and system state.

    Usage: `await system_context_service.add_system_context(payload)`
    """

    async def add_system_context(self, payload: Payload) -> Payload:
        """Add system context information to the project information state.

        Injects current date and other system-level metadata into the prompt
        context to help the agent maintain awareness of temporal information.

        Usage: `payload = await service.add_system_context(payload)`
        """

        state = payload.get("state", {})
        project_inforamtion_and_context = state.get(
            "project_inforamtion_and_context", []
        )

        project_inforamtion_and_context.append(
            (
                "user",
                dedent(f"""
                # System Context

                Current date: {datetime.now().strftime("%Y-%m-%d")}
                """),
            )
        )
        state["project_inforamtion_and_context"] = project_inforamtion_and_context

        return payload.set("state", state)
