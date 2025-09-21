from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.logging import log


class LintActor(Actor):
    async def handle_message(self, message: Message):
        log.info(msg=message)

    async def _handle_shutdown(self, message: Message):
        """Handle shutdown request"""
        pass

    async def setup_subscriptions(self, message_bus: MessageBus):
        message_bus.subscribe(LintActor, MessageType.DOMAIN_COMMAND)
