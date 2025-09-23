import asyncio
from typing import List

from rich.console import Console

from byte.core.actors.base import Actor
from byte.core.actors.message import (
    Message,
    MessageType,
)
from byte.domain.cli_input.prompt_handler import PromptHandler
from byte.domain.cli_input.service.command_registry import CommandRegistry
from byte.domain.cli_input.service.interactions_service import InteractionService


class InputActor(Actor):
    async def boot(self):
        await super().boot()
        self.pending_input_request = None  # Store pending input request
        self.current_state = (
            MessageType.REQUEST_USER_INPUT
        )  # Track current app state, start in idle
        self.active_tasks = set()  # Store active tasks for cancellation

    async def on_start(self):
        """Initialize prompt handler and start input loop"""
        self.prompt_handler = PromptHandler()
        await self.prompt_handler.initialize()

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
        if message.type == MessageType.REQUEST_USER_INPUT:
            self.current_state = MessageType.REQUEST_USER_INPUT
        elif message.type == MessageType.REQUEST_USER_CONFIRM:
            self.pending_input_request = message
            self.current_state = MessageType.REQUEST_USER_CONFIRM
        elif message.type == MessageType.SHUTDOWN:
            await self.stop()

    async def _handle_state_change(self, message: Message):
        """Handle state change notifications from CoordinatorActor"""
        self.current_state = message.payload.get("new_state")

    async def _input_loop(self):
        """State-driven input gathering loop"""

        while self.running:
            try:
                # Handle different states
                if self.current_state == MessageType.REQUEST_USER_INPUT:
                    # Normal input mode - show prompt
                    user_input = await self.prompt_handler.get_input_async("> ")
                    self.current_state = ""

                    if user_input.strip():
                        if user_input.startswith("/"):
                            # Send command - CoordinatorActor will handle state transition
                            task = asyncio.create_task(
                                self._handle_command_input(user_input)
                            )
                            self.active_tasks.add(task)
                            task.add_done_callback(self.active_tasks.discard)
                        else:
                            # Send to agent - CoordinatorActor will handle state transition
                            task = asyncio.create_task(self._send_to_agent(user_input))
                            self.active_tasks.add(task)
                            task.add_done_callback(self.active_tasks.discard)

                elif (
                    self.current_state == MessageType.REQUEST_USER_CONFIRM
                    and self.pending_input_request is not None
                ):
                    # Handle custom input request
                    request = self.pending_input_request
                    self.pending_input_request = None

                    # Use simple confirm for yes/no questions
                    message_text = request.payload.get("message", False)
                    default_value = request.payload.get("default", False)

                    interaction_service = await self.make(InteractionService)
                    user_input = await interaction_service.confirm(
                        message_text, default_value
                    )

                    # Send response back to requesting actor
                    if request.reply_to:
                        await request.reply_to.put(
                            Message(
                                type=MessageType.USER_RESPONSE,
                                payload={"input": user_input},
                            )
                        )

                    # Notify that user response was sent
                    await self.broadcast(
                        Message(
                            type=MessageType.USER_RESPONSE, payload={"completed": True}
                        )
                    )

                    self.current_state = None

                else:
                    # Unknown state or no state yet, wait briefly
                    await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                await self.broadcast(
                    Message(
                        type=MessageType.SHUTDOWN, payload={"reason": "user_interrupt"}
                    )
                )
                break
            except Exception as e:
                await self.on_error(e)

    async def _send_to_agent(self, user_input: str):
        """Send user input to agent actor"""
        from byte.domain.agent.actor.agent_actor import AgentActor

        await self.send_to(
            AgentActor,
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

        command_registry = await self.make(CommandRegistry)

        # Get the command object from the registry
        command = command_registry.get_slash_command(command_name)

        if command:
            # Execute the command directly
            try:
                await command.execute(args)
            except Exception as e:
                console = Console()
                console.print(
                    f"[red]Error executing command /{command_name}: {e}[/red]"
                )
        else:
            # Handle unknown command
            console = Console()
            console.print(f"[red]Unknown command: /{command_name}[/red]")

    async def get_completions(self, partial_input: str) -> List[str]:
        """Get completions by querying the command registry"""

        if not partial_input.startswith("/"):
            return []

        command_registry = await self.make(CommandRegistry)

        # Use the registry's built-in completion logic
        return await command_registry.get_slash_completions(partial_input)

    async def subscriptions(self):
        return [
            MessageType.SHUTDOWN,
            MessageType.REQUEST_USER_INPUT,
            MessageType.REQUEST_USER_CONFIRM,
            MessageType.REQUEST_USER_INPUT_TEXT,
        ]
