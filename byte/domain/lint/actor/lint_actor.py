from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.domain.lint.service import LintService


class LintActor(Actor):
    async def handle_message(self, message: Message):
        lint_service = await self.make(LintService)
        await lint_service.lint_changed_files()

    async def _handle_shutdown(self, message: Message):
        """Handle shutdown request"""
        pass

    async def subscriptions(self):
        return [
            MessageType.DOMAIN_COMMAND,
        ]
