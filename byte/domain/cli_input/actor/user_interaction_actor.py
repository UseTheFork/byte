from byte.core.actors.base import Actor
from byte.core.actors.message import (
    Message,
    MessageType,
)
from byte.domain.cli_input.service.interactions_service import InteractionService


class UserInteractionActor(Actor):
    """Dedicated actor for handling user confirmations, selections, and prompts"""

    async def handle_message(self, message: Message):
        if message.type == MessageType.REQUEST_USER_CONFIRM:
            await self._handle_confirmation(message)
        elif message.type == MessageType.REQUEST_USER_SELECT:
            await self._handle_selection(message)
        elif message.type == MessageType.REQUEST_USER_TEXT:
            await self._handle_text_input(message)

    async def _handle_confirmation(self, message: Message):
        """Handle confirmation requests with dedicated prompt session"""
        interaction_service = await self.make(InteractionService)

        prompt_text = message.payload.get("message", "Confirm?")
        default = message.payload.get("default", False)

        # Use a separate prompt session for interactions
        result = await interaction_service.confirm(prompt_text, default)

        # Send response back
        if message.reply_to:
            await message.reply_to.put(
                Message(type=MessageType.USER_RESPONSE, payload={"input": result})
            )

    async def _handle_selection(self, message: Message):
        pass

    async def _handle_text_input(self, message: Message):
        pass

    async def subscriptions(self):
        return [
            MessageType.SHUTDOWN,
            MessageType.REQUEST_USER_CONFIRM,
            MessageType.REQUEST_USER_SELECT,
            MessageType.REQUEST_USER_TEXT,
        ]
