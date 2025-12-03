from datetime import datetime

from byte.core.config.config import ByteConfg
from byte.core.event_bus import Payload
from byte.core.service.base_service import Service


class SystemContextService(Service):
    """Service for injecting system-level context into agent prompts.

    Provides current system information like dates and environment context
    that helps the AI agent maintain temporal awareness and system state.

    Usage: `await system_context_service.add_system_context(payload)`
    """

    async def add_system_context(self, payload: Payload) -> Payload:
        """Add system context information to the project context.

        Injects current date and other system-level metadata into the prompt
        context to help the agent maintain awareness of temporal information.

        Usage: `payload = await service.add_system_context(payload)`
        """
        system_context = []

        # Add current date
        system_context.append(f"- Current date: {datetime.now().strftime('%Y-%m-%d')}")

        # Check in the config if we have lint commands that should not be suggested.
        config = await self.make(ByteConfg)

        # Add lint commands context if configured
        if config.lint.enable and config.lint.commands:
            system_context.append("- The user's pre-commit runs these lint commands, don't suggest running them:")
            for lint_cmd in config.lint.commands:
                lint_cmd_string = " ".join(lint_cmd.command)
                exts = ", ".join(lint_cmd.languages)
                system_context.append(f"  - `{lint_cmd_string}` (for {exts} files)")

        system_context_list = payload.get("system_context", [])
        system_context_list.extend(system_context)
        payload.set("system_context", system_context_list)

        return payload
