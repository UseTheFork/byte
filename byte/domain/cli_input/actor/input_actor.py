import asyncio
from typing import Dict, List, Type

from rich.console import Console

from byte.core.actors.base import Actor
from byte.core.actors.message import (
    ExecuteCommand,
    GetCompletions,
    Message,
    MessageType,
)
from byte.domain.cli_input.prompt_handler import PromptHandler


class InputActor(Actor):
    async def boot(self):
        await super().boot()
        self.command_actors: Dict[str, Type[Actor]] = {}
        self.completion_handlers: Dict[str, Type[Actor]] = {}

    async def handle_message(self, message: Message):
        # Input actor primarily sends messages, doesn't handle many
        if message.type == MessageType.SHUTDOWN:
            await self.stop()

    async def on_start(self):
        """Initialize prompt handler and start input loop"""
        self.prompt_handler = PromptHandler()
        await self.prompt_handler.initialize()

        # Start input gathering in background
        self.input_task = asyncio.create_task(self._input_loop())

    async def on_stop(self):
        """Clean up input handling"""
        if self.input_task and not self.input_task.done():
            self.input_task.cancel()
            try:
                await self.input_task
            except asyncio.CancelledError:
                pass

    async def register_command_handler(
        self, command_name: str, actor_class: Type[Actor]
    ):
        """Register which actor handles a specific command"""
        self.command_actors[command_name] = actor_class

        # Also register for completions (commands that start with this name)
        self.completion_handlers[command_name] = actor_class

    async def get_completions(self, partial_input: str) -> List[str]:
        """Get completions by querying the appropriate actor"""
        if not partial_input.startswith("/"):
            return []

        # If user just typed "/", show all available commands
        if partial_input == "/":
            return [f"{cmd}" for cmd in self.command_actors.keys()]

        # Extract command name from partial input
        parts = partial_input[1:].split(" ", 1)  # Remove "/" and split on first space
        command_part = parts[0]

        # If we're still typing the command name, filter available commands
        if len(parts) == 1 and not partial_input.endswith(" "):
            matching_commands = [
                f"/{cmd}"
                for cmd in self.command_actors.keys()
                if cmd.startswith(command_part)
            ]
            return matching_commands

        # If command is complete and we have args, forward to the specific actor
        handler_actor = self.completion_handlers.get(command_part)
        if not handler_actor:
            return []

        # Query the actor for completions (for arguments/sub-commands)
        response_queue = asyncio.Queue()
        await self.send_to(
            handler_actor,
            GetCompletions(partial_input=partial_input, reply_to=response_queue),
        )

        try:
            response = await asyncio.wait_for(response_queue.get(), timeout=1.0)
            return response.completions if hasattr(response, "completions") else []
        except asyncio.TimeoutError:
            return []

    async def _input_loop(self):
        """Main input gathering loop with registered command routing"""
        from byte.domain.agent.actor.agent_actor import AgentActor

        while self.running:
            try:
                user_input = await self.prompt_handler.get_input_async("> ")

                if user_input.strip():
                    if user_input.startswith("/"):
                        await self._handle_command_input(user_input)
                    else:
                        await self.send_to(
                            AgentActor,
                            Message(
                                type=MessageType.USER_INPUT,
                                payload={"input": user_input},
                            ),
                        )
            except KeyboardInterrupt:
                await self.broadcast(
                    Message(
                        type=MessageType.SHUTDOWN, payload={"reason": "user_interrupt"}
                    )
                )
                break
            except Exception as e:
                await self.on_error(e)

    async def _handle_command_input(self, user_input: str):
        """Route command to registered actor"""
        parts = user_input.strip().split(None, 1)
        command_name = parts[0][1:]  # Remove leading '/'
        args = parts[1] if len(parts) > 1 else ""

        # Find registered actor for this command
        target_actor = self.command_actors.get(command_name)

        if target_actor:
            await self.send_to(
                target_actor,
                ExecuteCommand(
                    command_name=command_name, args=args, user_input=user_input
                ),
            )
        else:
            # Handle unknown command
            console = await self.make(Console)
            console.print(f"[red]Unknown command: /{command_name}[/red]")

    async def subscriptions(self):
        return [MessageType.SHUTDOWN]
