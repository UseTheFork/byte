from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession

from byte.core.config.config import BYTE_DIR
from byte.core.event_bus import EventType, Payload
from byte.core.service.base_service import Service
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli_input.prompt_handler import CommandCompleter
from byte.domain.cli_input.service.command_registry import CommandRegistry


class PromptToolkitService(Service):
    """ """

    async def boot(self):
        # Placeholder for `prompt_async` if we where interupted we restore using the placeholder
        self.placeholder = None
        self.interrupted = False

        self.completer = CommandCompleter()

        self.prompt_session = PromptSession(
            history=FileHistory(BYTE_DIR / ".input_history"),
            multiline=False,
            completer=self.completer,
        )

    async def execute(self):
        # Use placeholder if set, then clear it
        default = self.placeholder or ""
        self.placeholder = None
        self.interrupted = False

        message = "> "

        # Create payload with event type
        payload = Payload(
            event_type=EventType.PRE_PROMPT_TOOLKIT,
            data={
                "placeholder": self.placeholder,
                "interrupted": self.interrupted,
                "message": message,
            },
        )

        # Send the payload event and wait for systems to return as needed
        payload = await self.emit(payload)
        message = payload.get("message", message)

        user_input = await self.prompt_session.prompt_async(
            message=message, placeholder=default
        )
        # TODO: should we make `user_input` a [("user", user_input)], in this situation.

        agent_service = await self.make(AgentService)
        active_agent = agent_service.get_active_agent()

        payload = Payload(
            event_type=EventType.POST_PROMPT_TOOLKIT,
            data={
                "user_input": user_input,
                "interrupted": self.interrupted,
                "active_agent": active_agent,
            },
        )
        payload = await self.emit(payload)

        interrupted = payload.get("interrupted", self.interrupted)
        user_input = payload.get("user_input", user_input)
        active_agent = payload.get("active_agent", active_agent)

        # log.debug(payload)

        if not interrupted:
            if user_input.startswith("/"):
                await self._handle_command_input(user_input)
            else:
                await agent_service.execute_agent([("user", user_input)], active_agent)

    async def _handle_command_input(self, user_input: str):
        # Parse command name and args
        parts = user_input[1:].split(" ", 1)  # Remove "/" and split
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Get command registry and execute
        command_registry = await self.make(CommandRegistry)
        command = command_registry.get_slash_command(command_name)

        if command:
            await command.execute(args)
        else:
            print(f"Unknown command: /{command_name}")

    async def interrupt(self):
        if self.prompt_session and self.prompt_session.app:
            self.placeholder = self.prompt_session.app.current_buffer.text
            self.interrupted = True
            self.prompt_session.app.exit()
