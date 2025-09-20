import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Optional

from byte.core.actors.message import Message, MessageBus, MessageType


class Actor(ABC):
    def __init__(self, name: str, message_bus: MessageBus, container=None):
        self.name = name
        self.message_bus = message_bus
        self.container = container
        self.running = False
        self.inbox: Optional[asyncio.Queue] = None

        # Register with message bus
        message_bus.register_actor(name)
        self.inbox = message_bus.get_queue(name)

    async def start(self):
        """Start the actor's message processing loop"""
        self.running = True
        await self.on_start()

        while self.running:
            try:
                # Wait for message with timeout to allow periodic cleanup
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
        print(f"Actor {self.name} error: {error}")

    async def send_to(self, actor_name: str, message: Message):
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

    async def setup_subscriptions(self, message_bus: MessageBus):
        """Set up message subscriptions for this actor.

        Override in subclasses to define what message types this actor handles.
        This is called during the boot phase by the ServiceProvider.

        Usage: Override in subclass like:
        ```
        async def setup_subscriptions(self, message_bus: MessageBus):
            message_bus.subscribe(self.name, MessageType.USER_INPUT)
            message_bus.subscribe(self.name, MessageType.AGENT_REQUEST)
        ```
        """
        # Base implementation does nothing - subclasses override
        pass
