import asyncio
import threading
from typing import Any, Optional

from byte import Service
from byte.orchestration import BaseWorkflow
from byte.tui import Messages, Status


class WorkflowService(Service):
    """Service for executing workflows with compiled graphs."""

    def boot(self) -> None:
        """Initialize workflow service with cancel event and stream handlers."""
        self.cancel_event = threading.Event()

    def cancel(self) -> None:
        """Signal the current workflow execution to stop."""
        self.cancel_event.set()

    async def consume_messages(self, stream):
        async for event in stream:
            # if self.app.is_development:
            # self.app["log"].debug(event)

            if event["method"] != "messages":
                continue

            data = event["params"]["data"][0]
            metadata = event["params"]["data"][1] if len(event["params"]["data"]) > 1 else {}
            if not isinstance(data, dict):
                continue

            # namespace = event["params"]["namespace"]
            evt = data.get("event")

            # self.app["log"].info(event)

            match evt:
                case "message-start":
                    # Reset tracking state for a new message
                    # Optionally extract the node name from namespace
                    self.message_chunks = {}

                case "content-block-start":
                    block = data.get("content", {})
                    block_type = block.get("type")
                    index = data.get("index", 0)

                    if block_type == "text":
                        self.message_chunks[index] = {"type": "text", "completed": False}
                        self.emit_tui(Messages.Response(status=Status.PENDING, chunk=metadata.get("langgraph_node")))

                    elif block_type == "reasoning":
                        self.message_chunks[index] = {"type": "reasoning", "completed": False}
                        self.emit_tui(
                            Messages.ReasoningResponse(status=Status.PENDING, chunk=metadata.get("langgraph_node"))
                        )

                    elif block_type == "tool_use":
                        tool_id = block.get("id")
                        tool_name = block.get("name")
                        self.message_chunks[index] = {
                            "type": "tool_use",
                            "completed": False,
                            "id": tool_id,
                            "name": tool_name,
                        }
                        self.emit_tui(
                            Messages.ToolResponse(
                                status=Status.PENDING,
                                tool_name=tool_name,
                                tool_id=tool_id,
                            )
                        )

                    elif block_type == "tool_call_chunk":
                        tool_id = block.get("id")
                        tool_name = block.get("name")
                        self.message_chunks[index] = {
                            "type": "tool_call_chunk",
                            "completed": False,
                            "id": tool_id,
                            "name": tool_name,
                        }
                        self.emit_tui(
                            Messages.ToolResponse(
                                status=Status.PENDING,
                                tool_name=tool_name,
                                tool_id=tool_id,
                            )
                        )

                case "content-block-delta":
                    delta = data.get("delta", {})
                    delta_type = delta.get("type")
                    index = data.get("index", 0)

                    if delta_type == "text-delta":
                        self.emit_tui(
                            Messages.Response(
                                status=Status.RUNNING,
                                with_indicator=False,
                                chunk=delta.get("text", ""),
                            )
                        )

                    elif delta_type == "reasoning-delta":
                        self.emit_tui(
                            Messages.ReasoningResponse(
                                status=Status.RUNNING,
                                with_indicator=False,
                                chunk=delta.get("reasoning", ""),
                            )
                        )

                    elif delta_type == "input-json-delta":
                        tracked = self.message_chunks.get(index, {})
                        if "id" in tracked:
                            self.emit_tui(
                                Messages.ToolResponse(
                                    status=Status.RUNNING,
                                    tool_id=tracked["id"],
                                    with_indicator=False,
                                    chunk=delta.get("partial_json", ""),
                                )
                            )

                    elif delta_type == "block-delta":
                        fields = delta.get("fields", {})
                        if fields.get("type") == "tool_call_chunk":
                            tracked = self.message_chunks.get(index, {})
                            if "id" in tracked:
                                self.emit_tui(
                                    Messages.ToolResponse(
                                        status=Status.RUNNING,
                                        tool_id=tracked["id"],
                                        with_indicator=False,
                                        chunk=fields.get("args", ""),
                                    )
                                )

                case "content-block-finish":
                    index = data.get("index", 0)
                    tracked = self.message_chunks.get(index, {})
                    tracked["completed"] = True

                    if tracked.get("type") == "text":
                        self.emit_tui(Messages.Response(status=Status.SUCCESS))
                    elif tracked.get("type") == "reasoning":
                        self.emit_tui(Messages.ReasoningResponse(status=Status.SUCCESS))
                    elif tracked.get("type") in ("tool_use", "tool_call_chunk") and "id" in tracked:
                        self.emit_tui(
                            Messages.ToolResponse(
                                tool_id=tracked["id"],
                                status=Status.SUCCESS,
                            )
                        )

                case "message-finish":
                    # Capture usage metadata if present
                    usage = data.get("usage", {})
                    self.app["log"].info(f"[usage] {usage}")
                    # Safety net: close any blocks not yet finished
                    for idx, tracked in self.message_chunks.items():
                        if not tracked.get("completed"):
                            tracked["completed"] = True

    async def execute(
        self,
        workflow: BaseWorkflow,
        request: dict,
        thread_id: Optional[str] = None,
    ) -> dict[str, Any] | Any:
        """Execute a workflow with the provided request."""
        graph, initial_state, config = await workflow.compile(request, thread_id)

        # Reset Message chunks and our cancel Listener
        self.message_chunks = {}
        self.cancel_event = threading.Event()

        self.emit_tui(Messages.CreateHeading(workflow.human_name, "text-primary"))

        stream = await graph.astream_events(
            input=initial_state,
            config=config,
            version="v3",
        )

        await asyncio.gather(self.consume_messages(stream))

        return stream
