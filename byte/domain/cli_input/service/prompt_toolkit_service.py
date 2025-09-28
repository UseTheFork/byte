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
        self.completer = CommandCompleter()

        self.prompt_session = PromptSession(
            history=FileHistory(BYTE_DIR / ".input_history"),
            multiline=False,
            completer=self.completer,
        )

    async def execute(self):
        # Create payload with event type
        payload = Payload(event_type=EventType.PRE_PROMPT_TOOLKIT, data={})

        await self.emit(payload)

        user_input = await self.prompt_session.prompt_async("> ")

        if user_input.startswith("/"):
            print(user_input)
            await self._handle_command_input(user_input)
        else:
            await self._send_to_agent(user_input)

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

    async def _send_to_agent(self, user_input: str):
        agent_service = await self.make(AgentService)
        await agent_service.execute_current_agent([("user", user_input)])
        # log.info(result)
