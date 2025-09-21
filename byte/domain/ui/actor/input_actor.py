import asyncio

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.core.ui.prompt import PromptHandler
from byte.domain.system.actor.command_router_actor import CommandRouterActor


class InputActor(Actor):
    async def boot(self):
        await super().boot()
        self.prompt_handler = None
        self.input_task = None

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

    async def handle_message(self, message: Message):
        # Input actor primarily sends messages, doesn't handle many
        if message.type == MessageType.SHUTDOWN:
            await self.stop()

    async def _input_loop(self):
        """Main input gathering loop"""
        from byte.domain.agent.agent_actor import AgentActor

        while self.running:
            try:
                # Get user input (this will block until input is received)
                user_input = await self.prompt_handler.get_input_async("> ")

                if user_input.strip():
                    # Determine if this is a command or regular input
                    if user_input.startswith("/"):
                        await self.send_to(
                            CommandRouterActor,
                            Message(
                                type=MessageType.COMMAND_INPUT,
                                payload={"input": user_input},
                            ),
                        )
                    else:
                        await self.send_to(
                            AgentActor,
                            Message(
                                type=MessageType.USER_INPUT,
                                payload={"input": user_input},
                            ),
                        )

            except KeyboardInterrupt:
                # User wants to exit
                await self.broadcast(
                    Message(
                        type=MessageType.SHUTDOWN, payload={"reason": "user_interrupt"}
                    )
                )
                break
            except Exception as e:
                await self.on_error(e)

    async def subscriptions(self):
        return [MessageType.SHUTDOWN]
