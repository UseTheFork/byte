import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from byte.core.actors.message import Message, MessageType


class StreamState(Enum):
    IDLE = "idle"
    STARTING = "starting"
    STREAMING = "streaming"
    PAUSED = "paused"
    FINISHING = "finishing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class StreamMetadata:
    stream_id: str
    stream_type: str
    created_at: float
    agent_type: Optional[str] = None
    user_input: Optional[str] = None


class StreamPipeline:
    def __init__(
        self, stream_id: str, output_queue: asyncio.Queue, metadata: StreamMetadata
    ):
        self.stream_id = stream_id
        self.output_queue = output_queue
        self.metadata = metadata
        self.state = StreamState.IDLE
        self.buffer: List[str] = []
        self.accumulated_content = ""
        self.error: Optional[Exception] = None
        self.cancelled = False

    async def start(self):
        """Start the stream pipeline"""
        if self.state != StreamState.IDLE:
            raise ValueError(f"Cannot start stream in state {self.state}")

        self.state = StreamState.STARTING
        await self.output_queue.put(
            Message(
                type=MessageType.START_STREAM,
                payload={
                    "stream_id": self.stream_id,
                    "metadata": self.metadata,
                    "timestamp": time.time(),
                },
            )
        )
        self.state = StreamState.STREAMING

    async def process_chunk(self, chunk_data: Any):
        """Process a chunk of data from the agent stream"""
        if self.cancelled or self.state not in [
            StreamState.STREAMING,
            StreamState.PAUSED,
        ]:
            return

        # {'event': 'on_chat_model_stream', 'data': {'chunk':                 streams.py:70
        #             AIMessageChunk(content=[{'text': ' concepts\n\nWhat would you like
        #             me', 'type': 'text', 'index': 0}], additional_kwargs={},
        #             response_metadata={},
        #             id='run--4e2b7aef-0ac4-4736-95bb-7377adaa6a70')}, 'run_id':
        #             '4e2b7aef-0ac4-4736-95bb-7377adaa6a70', 'name': 'ChatAnthropic',
        #             'tags': ['seq:step:2'], 'metadata': {'thread_id':
        #             '22c18f71-84a4-42ec-a513-774da8ef51cc', 'langgraph_step': 2,
        #             'langgraph_node': 'assistant', 'langgraph_triggers':
        #             ('branch:to:assistant',), 'langgraph_path': ('__pregel_pull',
        #             'assistant'), 'langgraph_checkpoint_ns':
        #             'assistant:e10be268-236c-2939-d303-2645a6625a98', 'checkpoint_ns':
        #             'assistant:e10be268-236c-2939-d303-2645a6625a98', 'ls_provider':
        #             'anthropic', 'ls_model_name': 'claude-sonnet-4-20250514',
        #             'ls_model_type': 'chat', 'ls_temperature': 0.1, 'ls_max_tokens':
        #             1024}, 'parent_ids': ['3ae0338a-0450-4d31-84cf-8277d627cb62',
        #             '7b6ea15d-3f1e-4454-a46e-c6564258e0bb',
        #             'ef6ee36c-e5a5-4bcf-8cce-d51d86e8b2e7']}

        # Extract text content
        text_content = self._extract_text_content(chunk_data.get("data").get("chunk"))
        # log.info(text_content)

        if text_content:
            self.buffer.append(text_content)
            self.accumulated_content += text_content

            # Send chunk to renderer
            await self.output_queue.put(
                Message(
                    type=MessageType.STREAM_CHUNK,
                    payload={
                        "stream_id": self.stream_id,
                        "chunk": text_content,
                        "accumulated": self.accumulated_content,
                        "chunk_data": chunk_data,  # Include original for event type detection
                        "timestamp": time.time(),
                    },
                )
            )

    async def finish(self, final_message=None):
        """Finish the stream"""
        if self.cancelled:
            return

        self.state = StreamState.FINISHING
        await self.output_queue.put(
            Message(
                type=MessageType.END_STREAM,
                payload={
                    "stream_id": self.stream_id,
                    "final_content": self.accumulated_content,
                    "final_message": final_message,
                    "timestamp": time.time(),
                },
            )
        )
        self.state = StreamState.COMPLETED

    async def cancel(self):
        """Cancel the stream"""
        self.cancelled = True
        self.state = StreamState.CANCELLED
        await self.output_queue.put(
            Message(
                type=MessageType.CANCEL_STREAM,
                payload={"stream_id": self.stream_id, "timestamp": time.time()},
            )
        )

    async def error(self, exception: Exception):
        """Handle stream error"""
        self.error = exception
        self.state = StreamState.ERROR
        await self.output_queue.put(
            Message(
                type=MessageType.STREAM_ERROR,
                payload={
                    "stream_id": self.stream_id,
                    "error": str(exception),
                    "timestamp": time.time(),
                },
            )
        )

    def pause(self):
        """Pause the stream"""
        if self.state == StreamState.STREAMING:
            self.state = StreamState.PAUSED

    def resume(self):
        """Resume the stream"""
        if self.state == StreamState.PAUSED:
            self.state = StreamState.STREAMING

    def _extract_text_content(self, chunk) -> str:
        """Extract text content from LLM chunk - your existing logic"""
        if hasattr(chunk, "content"):
            if isinstance(chunk.content, str):
                return chunk.content
            elif isinstance(chunk.content, list) and chunk.content:
                text_parts = []
                for item in chunk.content:
                    if isinstance(item, dict):
                        if item.get("type") == "text" and "text" in item:
                            text_parts.append(item["text"])
                        elif "text" in item and item.get("type") != "input_json_delta":
                            text_parts.append(item["text"])
                    elif isinstance(item, str):
                        text_parts.append(item)
                return "".join(text_parts)
        return ""


class StreamManager:
    def __init__(self, rendering_queue: asyncio.Queue):
        self.rendering_queue = rendering_queue
        self.active_streams: Dict[str, StreamPipeline] = {}
        self.stream_counter = 0

    def create_stream(
        self,
        stream_type: str,
        agent_type: Optional[str] = None,
        user_input: Optional[str] = None,
    ) -> str:
        """Create a new stream and return its ID"""
        self.stream_counter += 1
        stream_id = f"{stream_type}_{self.stream_counter}_{int(time.time() * 1000)}"

        metadata = StreamMetadata(
            stream_id=stream_id,
            stream_type=stream_type,
            created_at=time.time(),
            agent_type=agent_type,
            user_input=user_input,
        )

        pipeline = StreamPipeline(stream_id, self.rendering_queue, metadata)
        self.active_streams[stream_id] = pipeline
        return stream_id

    async def start_stream(self, stream_id: str):
        """Start a stream"""
        if stream_id in self.active_streams:
            await self.active_streams[stream_id].start()

    async def process_chunk(self, stream_id: str, chunk_data: Any):
        """Process a chunk for a specific stream"""
        if stream_id in self.active_streams:
            await self.active_streams[stream_id].process_chunk(chunk_data)

    async def finish_stream(self, stream_id: str, final_message=None):
        """Finish a stream"""
        if stream_id in self.active_streams:
            await self.active_streams[stream_id].finish(final_message)
            # Keep stream for a bit for potential cleanup

    async def cancel_stream(self, stream_id: str):
        """Cancel a stream"""
        if stream_id in self.active_streams:
            await self.active_streams[stream_id].cancel()

    def cleanup_completed_streams(self):
        """Remove completed streams"""
        completed = [
            sid
            for sid, stream in self.active_streams.items()
            if stream.state
            in [StreamState.COMPLETED, StreamState.CANCELLED, StreamState.ERROR]
        ]
        for stream_id in completed:
            del self.active_streams[stream_id]

    def get_active_streams(self) -> List[str]:
        """Get list of active stream IDs"""
        return [
            sid
            for sid, stream in self.active_streams.items()
            if stream.state in [StreamState.STREAMING, StreamState.PAUSED]
        ]
