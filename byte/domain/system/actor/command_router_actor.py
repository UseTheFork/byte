from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.logging import log
from byte.domain.lint.actor.lint_actor import LintActor
from byte.domain.system.actor.system_command_actor import SystemCommandActor


class CommandRouterActor(Actor):
    """Routes commands to appropriate domain actors based on command type"""

    async def handle_message(self, message: Message):
        if message.type == MessageType.COMMAND_INPUT:
            await self._route_command(message)

    async def _route_command(self, message: Message):
        user_input = message.payload.get("input", "")
        parts = user_input.strip().split(None, 1)
        command_name = parts[0][1:]
        args = parts[1] if len(parts) > 1 else ""

        # Route to appropriate domain actor
        domain_actor = self._get_domain_actor_for_command(command_name)

        if domain_actor:
            await self.send_to(
                domain_actor,
                Message(
                    type=MessageType.DOMAIN_COMMAND,
                    payload={
                        "command": command_name,
                        "args": args,
                        "original_input": user_input,
                    },
                ),
            )
        else:
            # Handle unknown command
            await self._handle_unknown_command(command_name)

    async def _handle_unknown_command(self, command_name: str):
        log.info(command_name)

    def _get_domain_actor_for_command(self, command_name: str):
        """Map commands to their domain actors"""
        command_routing = {
            # "add": FileCommandActor,
            # "drop": FileCommandActor,
            # "read-only": FileCommandActor,
            "exit": SystemCommandActor,
            # "help": SystemCommandActor,
            # "agent": AgentCommandActor,
            # "coder": AgentCommandActor,
            # "commit": GitCommandActor,
            "lint": LintActor,
        }
        return command_routing.get(command_name)

    async def setup_subscriptions(self, message_bus: MessageBus):
        message_bus.subscribe(CommandRouterActor, MessageType.COMMAND_INPUT)
