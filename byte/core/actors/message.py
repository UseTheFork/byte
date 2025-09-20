import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from byte.container import Container
from byte.core.logging import log
from byte.core.service.mixins import Bootable


class MessageType(Enum):
    # User interaction
    USER_INPUT = "user_input"
    COMMAND_INPUT = "command_input"

    # Agent processing
    AGENT_REQUEST = "agent_request"
    AGENT_RESPONSE = "agent_response"

    # Stream management
    START_STREAM = "start_stream"
    STREAM_CHUNK = "stream_chunk"
    END_STREAM = "end_stream"
    STREAM_ERROR = "stream_error"
    CANCEL_STREAM = "cancel_stream"

    # Tool execution
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    TOOL_ERROR = "tool_error"

    # File system
    FILE_CHANGE = "file_change"
    FILE_ADDED = "file_added"
    FILE_REMOVED = "file_removed"

    # System
    SHUTDOWN = "shutdown"
    STATE_CHANGE = "state_change"
    ERROR = "error"


@dataclass
class Message:
    type: MessageType
    payload: Dict[str, Any]
    reply_to: Optional[asyncio.Queue] = None
    correlation_id: Optional[str] = None


class MessageBus(Bootable):
    def __init__(self, container: Optional["Container"] = None):
        super().__init__(container)
        self.queues: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[MessageType, list[str]] = {}

    def register_actor(self, actor_name: str, queue_size: int = 100):
        """Register an actor with the message bus"""
        self.queues[actor_name] = asyncio.Queue(maxsize=queue_size)

    def subscribe(self, actor_name: str, message_type: MessageType):
        """Subscribe an actor to a message type"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(actor_name)

    async def send_to(self, actor_name: str, message: Message):
        """Send message to specific actor"""
        log.info(message)
        if actor_name in self.queues:
            await self.queues[actor_name].put(message)
        else:
            raise ValueError(f"Actor {actor_name} not registered")

    async def broadcast(self, message: Message):
        """Broadcast message to all subscribers"""
        if message.type in self.subscribers:
            for actor_name in self.subscribers[message.type]:
                await self.send_to(actor_name, message)

    def get_queue(self, actor_name: str) -> asyncio.Queue:
        """Get queue for an actor"""
        return self.queues.get(actor_name)
