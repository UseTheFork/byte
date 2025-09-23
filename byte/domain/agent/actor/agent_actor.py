import asyncio

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.core.actors.streams import StreamManager
from byte.core.service.mixins import UserInteractive
from byte.domain.agent.coder.agent import CoderAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli_output.actor.rendering_actor import RenderingActor


class AgentActor(Actor, UserInteractive):
    async def boot(self):
        await super().boot()
        self.stream_manager = StreamManager(self.message_bus.get_queue(RenderingActor))

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
        """Process agent request without blocking main actor loop"""
        try:
            # Start the stream
            await self.stream_manager.start_stream(stream_id)

            # Get agent service
            agent_service = await self.make(AgentService)

            # Route to appropriate agent (defaulting to CoderAgent for now)
            agent_class = CoderAgent  # This would be dynamic based on agent_type

            # Get the agent stream
            agent_stream = agent_service.route_to_agent(agent_class, user_input)

            # Process stream events
            final_message = None
            async for event in agent_stream:
                await self.stream_manager.process_chunk(stream_id, event)

                # Extract final message if this is the end event
                if (
                    event.get("event") == "on_chain_end"
                    and event.get("name") == "LangGraph"
                ):
                    messages = event["data"]["output"]["messages"]
                    final_message = messages[-1] if messages else None

            # Finish the stream
            await self.stream_manager.finish_stream(stream_id, final_message)

        except Exception as e:
            # Handle stream error
            if stream_id in self.stream_manager.active_streams:
                await self.stream_manager.active_streams[stream_id].error(e)
        finally:
            # Cleanup completed streams periodically
            self.stream_manager.cleanup_completed_streams()
            await self.prompt_for_input()

    async def subscriptions(self):
        return [
            MessageType.SHUTDOWN,
            MessageType.USER_INPUT,
            MessageType.AGENT_REQUEST,
            MessageType.CANCEL_STREAM,
        ]
