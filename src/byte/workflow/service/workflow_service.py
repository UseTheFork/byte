from typing import Any, Literal, Optional

from langchain_core.callbacks import get_usage_metadata_callback

from byte import Service
from byte.analytics import AgentAnalyticsService
from byte.orchestration import TokenUsageSchema
from byte.tui import Messages
from byte.workflow import BaseWorkflow


class WorkflowService(Service):
    """Service for executing workflows with compiled graphs."""

    def _is_tool_call_chunk(self, block: dict) -> bool:
        return block.get("type") in ("tool_use", "input_json_delta")

    def _is_message_content_chunk(self, block: dict) -> bool:
        return block.get("type") == "text"

    async def _track_token_usage(self, usage_metadata: dict, mode: str) -> None:
        """Track token usage from callback metadata and update analytics.

        Extracts usage metadata from the get_usage_metadata_callback result
        and records it in the analytics service based on the current AI mode.

        Args:
            usage_metadata: Dictionary with model names as keys and usage stats as values
            mode: The AI mode being used ("main" or "weak")

        Usage: `await self._track_token_usage(cb, runtime.context.mode)`
        """
        if usage_metadata:
            # Get the first model's usage data (typically only one model)
            model_usage = next(iter(usage_metadata.values()))

            usage = TokenUsageSchema(
                input_tokens=model_usage.get("input_tokens", 0),
                output_tokens=model_usage.get("output_tokens", 0),
                total_tokens=model_usage.get("total_tokens", 0),
            )
            agent_analytics_service = self.app.make(AgentAnalyticsService)
            if mode == "main":
                await agent_analytics_service.update_main_usage(usage)
            else:
                await agent_analytics_service.update_weak_usage(usage)

    async def _handle_stream_event(self, chunk: dict[str, Any] | Any):
        """Handle individual stream events for display and final message extraction.

        Args:
                mode: The stream mode ("values", "updates", "messages", or "custom")
                chunk: The data chunk from that stream mode
        """

        if chunk["type"] == "messages":
            message_chunk, metadata = chunk["data"]

            msg_type = type(message_chunk).__name__
            self.app["log"].debug(f"Message chunk type: {msg_type}")
            self.app["log"].debug(message_chunk)

            for block in message_chunk.content:
                if isinstance(block, dict):
                    if self._is_tool_call_chunk(block):
                        pass
                    elif self._is_message_content_chunk(block):
                        await self.emit_tui(Messages.ResponseChunk(block.get("text", "")))

        elif chunk["type"] == "tasks":
            pass
            # tui.post_message(Messages.CommandStreamChunk(panel_id=self.panel_id, chunk_type="task", data=chunk["data"]))

        # elif chunk["type"] == "tasks":
        #     await stream_rendering_service.handle_task(chunk["data"])
        #     # self.app["log"].debug(chunk)
        #     # self.app["log"].debug(chunk.get("id"))
        #     # self.app["log"].debug(chunk.get("name"))

        return chunk

    async def execute(
        self,
        workflow: BaseWorkflow,
        request: dict,
        thread_id: Optional[str] = None,
        display_mode: Literal["verbose", "thinking", "silent"] = "verbose",
    ):
        """Execute a workflow with the provided request.

        Args:
            workflow: The workflow to execute
            request: The user request to process
            thread_id: Optional thread ID for conversation context

        Usage: `await workflow_service.execute(ask_workflow, "How do I...?")`
        """
        graph, initial_state, config = await workflow.compile(request, thread_id)

        # TODO: Do we need this?
        # Emit workflow start event
        # await self.emit(
        #     Payload(
        #         event_type=EventType.WORKFLOW_STARTED,
        #         data={"workflow": workflow.__class__.__name__, "thread_id": thread_id},
        #     )
        # )

        processed_event = None
        with get_usage_metadata_callback() as usage_metadata_callback:
            async for chunk in graph.astream(
                input=initial_state,
                config=config,
                stream_mode=["messages", "tasks"],
                version="v2",
                subgraphs=True,
            ):
                processed_event = await self._handle_stream_event(chunk)

            # await event_bus.emit(Events.TextualMessageReceived(Messages.AgentResponseComplete()))

            # TODO: need to use `processed_event` to figure out what mode we are in.
            await self._track_token_usage(usage_metadata_callback.usage_metadata, "main")

        # await self.event_handler(Messages.AgentResponseComplete())
        return processed_event
