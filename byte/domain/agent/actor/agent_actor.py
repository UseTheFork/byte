import asyncio
from typing import Dict

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.core.actors.streams import StreamManager
from byte.core.logging import log
from byte.core.service.mixins import UserInteractive
from byte.domain.agent.coder.agent import CoderAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli_output.actor.rendering_actor import RenderingActor
from byte.domain.system.actor.coordinator_actor import CoordinatorActor


class AgentActor(Actor, UserInteractive):
    async def boot(self):
        await super().boot()
        self.stream_manager = StreamManager(self.message_bus.get_queue(RenderingActor))
        # Track accumulated tool call chunks for proper parsing
        self.accumulated_tool_calls: Dict[str, Dict] = {}

    async def handle_message(self, message: Message):
        if message.type == MessageType.SHUTDOWN:
            await self.stop()
        elif message.type == MessageType.USER_INPUT:
            await self._handle_user_input(message)
        elif message.type == MessageType.AGENT_REQUEST:
            await self._handle_agent_request(message)
        elif message.type == MessageType.CANCEL_STREAM:
            await self._handle_cancel_stream(message)

    async def _handle_user_input(self, message: Message):
        """Handle user input by routing to appropriate agent"""
        user_input = message.payload["input"]
        agent_type = message.payload.get("agent_type", "coder")

        await self.send_to(
            CoordinatorActor,
            Message(
                type=MessageType.AGENT_REQUEST,
                payload={
                    "action": "start_thinking",
                    "agent_type": agent_type,
                    "user_input": user_input,
                },
            ),
        )

        # Create new stream for this request
        stream_id = self.stream_manager.create_stream(
            stream_type="agent", agent_type=agent_type, user_input=user_input
        )

        # Start processing in background
        asyncio.create_task(
            self._process_agent_request(stream_id, agent_type, user_input)
        )

    async def _handle_agent_request(self, message: Message):
        """Handle direct agent requests"""
        # Similar to user input but for programmatic requests
        pass

    async def _handle_cancel_stream(self, message: Message):
        """Handle stream cancellation requests"""
        stream_id = message.payload.get("stream_id")
        if stream_id:
            await self.stream_manager.cancel_stream(stream_id)

    async def _process_agent_request(
        self, stream_id: str, agent_type: str, user_input: str
    ):
        """Process agent request using astream_events for comprehensive streaming"""
        try:
            # Start the stream
            await self.stream_manager.start_stream(stream_id)

            await self.send_to(
                CoordinatorActor,
                Message(
                    type=MessageType.START_STREAM,
                    payload={"stream_id": stream_id, "agent_type": agent_type},
                ),
            )

            # Get agent service and create the runnable
            agent_service = await self.make(AgentService)
            agent_class = CoderAgent  # This would be dynamic based on agent_type

            # Get the agent runnable (not the old stream method)
            agent_runnable = await agent_service.get_agent_runnable(agent_class)

            # Clear any previous tool call state for this stream
            self.accumulated_tool_calls.clear()

            # Use astream_events for comprehensive streaming
            async for event in agent_runnable.astream_events(
                user_input,
                include_types=["chat_model", "tool"],  # Filter relevant events
            ):
                await self._handle_stream_event(stream_id, event)

            # Finish the stream
            await self.stream_manager.finish_stream(stream_id)

            await self.send_to(
                CoordinatorActor,
                Message(
                    type=MessageType.END_STREAM,
                    payload={"stream_id": stream_id, "success": True},
                ),
            )

        except Exception as e:
            log.error(f"Agent processing error: {e}")
            # Handle stream error
            if stream_id in self.stream_manager.active_streams:
                await self.stream_manager.active_streams[stream_id].error(e)

            await self.send_to(
                CoordinatorActor,
                Message(
                    type=MessageType.STREAM_ERROR,
                    payload={"stream_id": stream_id, "error": str(e)},
                ),
            )

        finally:
            # Cleanup completed streams periodically
            self.stream_manager.cleanup_completed_streams()
            await self.prompt_for_input()

    async def _handle_stream_event(self, stream_id: str, event: dict):
        """Route different event types to appropriate handlers"""
        event_type = event["event"]

        if event_type == "on_chat_model_stream":
            await self._handle_chat_model_stream(stream_id, event)
        elif event_type == "on_chat_model_start":
            # Model started thinking - could show spinner
            pass
        elif event_type == "on_tool_start":
            await self._handle_tool_start(stream_id, event)
        elif event_type == "on_tool_end":
            await self._handle_tool_end(stream_id, event)

    async def _handle_chat_model_stream(self, stream_id: str, event: dict):
        """Handle streaming chunks from the chat model"""
        chunk = event["data"]["chunk"]

        # Handle tool call chunks if present
        if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
            await self._handle_tool_call_chunks(stream_id, chunk.tool_call_chunks)

        # Handle regular text content
        text_content = self._extract_text_content(chunk)
        if text_content:
            await self.stream_manager.process_chunk(
                stream_id, {"data": {"chunk": chunk}, "type": "text"}
            )

    async def _handle_tool_call_chunks(self, stream_id: str, tool_call_chunks: list):
        """Handle streaming tool call chunks with accumulation"""
        for tool_chunk in tool_call_chunks:
            tool_id = tool_chunk.get("id")
            tool_name = tool_chunk.get("name")
            tool_args = tool_chunk.get("args", "")
            index = tool_chunk.get("index", 0)

            # Create unique key for this tool call
            call_key = f"{tool_id}_{index}" if tool_id else f"unknown_{index}"

            # Initialize or update accumulated state
            if call_key not in self.accumulated_tool_calls:
                self.accumulated_tool_calls[call_key] = {
                    "id": tool_id,
                    "name": tool_name,
                    "args": "",
                    "index": index,
                    "complete": False,
                }

            # Accumulate arguments
            if tool_args:
                self.accumulated_tool_calls[call_key]["args"] += tool_args

            # Update name if we didn't have it before
            if tool_name and not self.accumulated_tool_calls[call_key]["name"]:
                self.accumulated_tool_calls[call_key]["name"] = tool_name

            # Broadcast tool call chunk for real-time display
            await self.broadcast(
                Message(
                    type=MessageType.TOOL_CALL_CHUNK,
                    payload={
                        "stream_id": stream_id,
                        "tool_name": self.accumulated_tool_calls[call_key]["name"],
                        "tool_args": self.accumulated_tool_calls[call_key]["args"],
                        "tool_id": tool_id,
                        "index": index,
                        "is_partial": True,
                        "call_key": call_key,
                    },
                )
            )

    async def _handle_tool_start(self, stream_id: str, event: dict):
        """Handle tool execution start"""
        tool_name = event["name"]
        await self.broadcast(
            Message(
                type=MessageType.TOOL_START,
                payload={
                    "tool_name": tool_name,
                    "stream_id": stream_id,
                    "event_data": event,
                },
            )
        )

    async def _handle_tool_end(self, stream_id: str, event: dict):
        """Handle tool execution completion"""
        tool_name = event["name"]
        tool_output = event["data"].get("output")

        await self.broadcast(
            Message(
                type=MessageType.TOOL_END,
                payload={
                    "tool_name": tool_name,
                    "stream_id": stream_id,
                    "tool_output": tool_output,
                    "event_data": event,
                },
            )
        )

    def _extract_text_content(self, chunk) -> str:
        """Extract text content from LLM chunk"""
        if hasattr(chunk, "content"):
            if isinstance(chunk.content, str):
                return chunk.content
            elif isinstance(chunk.content, list):
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

    async def subscriptions(self):
        return [
            MessageType.SHUTDOWN,
            MessageType.USER_INPUT,
            MessageType.AGENT_REQUEST,
            MessageType.CANCEL_STREAM,
        ]
