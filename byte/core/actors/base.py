import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, TypeVar

from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.service.mixins import Bootable, Injectable

T = TypeVar("T")


class Actor(ABC, Bootable, Injectable):
    async def boot(self):
        self.name = self.__class__
        self.message_bus = await self.make(MessageBus)
        self.running = False
        self.inbox: Optional[asyncio.Queue] = None

        # Register with message bus
        self.message_bus.register_actor(self.name)
        self.inbox = self.message_bus.get_queue(self.name)

    async def start(self):
        """Start the actor's message processing loop"""
        self.running = True
        await self.on_start()

        while self.running:
            try:
                # Wait for message with timeout to allow periodic cleanup
                if self.inbox is None:
                    await asyncio.sleep(0.1)  # Brief wait for initialization
                    continue

                message = await asyncio.wait_for(self.inbox.get(), timeout=1.0)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                # Periodic maintenance
                await self.on_idle()
            except Exception as e:
                await self.on_error(e)

        await self.on_stop()

    async def stop(self):
        """Stop the actor"""
        self.running = False

    @abstractmethod
    async def handle_message(self, message: Message):
        """Handle incoming messages - must be implemented by subclasses"""
        pass

    async def on_start(self):
        """Called when actor starts - override for initialization"""
        pass

    async def on_stop(self):
        """Called when actor stops - override for cleanup"""
        pass

    async def on_idle(self):
        """Called during idle periods - override for maintenance"""
        pass

    async def on_error(self, error: Exception):
        """Called when an error occurs - override for error handling"""
        print(f"Actor {self.__class__} error: {error}")

    async def send_to(self, actor_name: Type[T], message: Message):
        """Send message to another actor"""
        await self.message_bus.send_to(actor_name, message)

    async def broadcast(self, message: Message):
        """Broadcast message to all subscribers"""
        await self.message_bus.broadcast(message)

    async def reply(self, original_message: Message, response_payload: Dict):
        """Reply to a message"""
        if original_message.reply_to:
            response = Message(
                type=MessageType.AGENT_RESPONSE,
                payload=response_payload,
                correlation_id=original_message.correlation_id,
            )
            await original_message.reply_to.put(response)

    def generate_correlation_id(self) -> str:
        """Generate unique correlation ID for message tracking"""
        return str(uuid.uuid4())

    async def subscriptions(self):
        """Set up message subscriptions for this actor.

        Override in subclasses to define what message types this actor handles.
        This is called during the boot phase by the ServiceProvider.

        Returns:
            List[MessageType]: List of message types this actor subscribes to
        """
        # Base implementation does nothing - subclasses override
        return []
