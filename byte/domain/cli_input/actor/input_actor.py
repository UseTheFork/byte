import asyncio
from typing import List

from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console

from byte.core.actors.base import Actor
from byte.core.actors.message import (
    Message,
    MessageType,
)
from byte.core.config.config import BYTE_DIR
from byte.domain.cli_input.prompt_handler import CommandCompleter
from byte.domain.cli_input.service.command_registry import CommandRegistry


class InputActor(Actor):
    async def boot(self):
        await super().boot()

        self.prompt_session = None

        self.pending_input_request = None  # Store pending input request
        self.current_state = "idle"  # Track current app state, start in idle
        self.active_tasks = set()  # Store active tasks for cancellation

    async def on_start(self):
        """Initialize prompt handler and start input loop"""

        self.completer = CommandCompleter()

        self.prompt_session = PromptSession(
            history=FileHistory(BYTE_DIR / ".input_history"),
            multiline=False,
            completer=self.completer,
        )

        # Start input gathering in background
        self.input_task = asyncio.create_task(self._input_loop())

    async def on_stop(self):
        """Clean up input handling"""
        # Cancel all active tasks
        for task in self.active_tasks.copy():
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete or be cancelled
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

        if self.input_task and not self.input_task.done():
            self.input_task.cancel()
            try:
                await self.input_task
            except asyncio.CancelledError:
                pass

    async def handle_message(self, message: Message):
        if message.type == MessageType.STATE_CHANGE:
            await self._handle_state_change(message)

        if message.type == MessageType.USER_INPUT:
            self.current_state = MessageType.USER_INPUT

        elif message.type == MessageType.SHUTDOWN:
            await self.stop()

    async def _handle_state_change(self, message: Message):
        """Handle state change notifications from CoordinatorActor"""
        self.current_state = message.payload.get("new_state")

    async def _input_loop(self):
        console = await self.make(Console)
        while self.running:
            await asyncio.sleep(0.1)
            if self.current_state == "idle":
                # Only handle normal input - no complex state switching
                console.rule()
                user_input = await self.prompt_session.prompt_async("> ")

                if user_input.startswith("/"):
                    await self._handle_command_input(user_input)
                else:
                    await self._send_to_agent(user_input)
            else:
                # Just wait when not in idle state
                await asyncio.sleep(0.5)

    async def _send_to_agent(self, user_input: str):
        """Send user input to agent actor"""

        if not user_input.strip():
            return

        # State changes dont happend fast enough
        self.current_state = ""
        await self.broadcast(
            Message(
                type=MessageType.USER_INPUT,
                payload={"input": user_input},
            ),
        )

    async def _handle_command_input(self, user_input: str):
        """Route command to registered actor"""

        parts = user_input.strip().split(None, 1)
        command_name = parts[0][1:]  # Remove leading '/'
        args = parts[1] if len(parts) > 1 else ""

        console = await self.make(Console)
        command_registry = await self.make(CommandRegistry)
        # Get the command object from the registry
        command = command_registry.get_slash_command(command_name)

        if command:
            try:
                await self.broadcast(
                    Message(
                        type=MessageType.COMMAND_INPUT,
                        payload={"command_name": command_name},
                    )
                )
                await asyncio.sleep(0.01)
                await command.execute(args)
                # Signal completion after successful execution
                await self.broadcast(
                    Message(
                        type=MessageType.COMMAND_COMPLETED,
                        payload={"command_name": command_name},
                    )
                )
            except Exception as e:
                console.print(
                    f"[red]Error executing command /{command_name}: {e}[/red]"
                )
                # Could send COMMAND_FAILED message here if needed
        else:
            console.print(f"[red]Unknown command: /{command_name}[/red]")

    async def get_completions(self, partial_input: str) -> List[str]:
        """Get completions by querying the command registry"""

        if not partial_input.startswith("/"):
            return []

        command_registry = await self.make(CommandRegistry)

        # Use the registry's built-in completion logic
        return await command_registry.get_slash_completions(partial_input)

    async def subscriptions(self):
        return [MessageType.SHUTDOWN, MessageType.STATE_CHANGE, MessageType.USER_INPUT]
