import shutil
from typing import List

from langchain_core.messages import BaseMessage
from langgraph.graph.state import RunnableConfig

from byte.support import Service


class RecordResponseService(Service):
    """Record assistant responses to disk for debugging."""

    async def record_response(
        self,
        messages: List[BaseMessage] | None,
        config: RunnableConfig,
    ):
        """Write assistant response to a cache file."""

        if not messages:
            return

        metadata = config.get("metadata", {})
        workflow_name = metadata.get("workflow", "")
        langgraph_node = metadata.get("langgraph_node")
        langgraph_step = metadata.get("langgraph_step")

        cache_file = self.app.cache_path(f"conversations/{workflow_name}/{langgraph_step}_{langgraph_node}.md")

        # Ensure cache directory exists
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        content_parts = []
        for message in messages:
            message_type = type(message).__name__
            content_parts.append(f"======== {message_type} ========")
            # TODO: The below should check if its a dict and if it is use json dumps to make it pretty etc.
            content_parts.append(str(message.text))
            content_parts.append("")

            if hasattr(message, "tool_calls") and message.tool_calls:
                content_parts.append("Tool Calls:")
                for tool_call in message.tool_calls:
                    tool_name = (
                        tool_call.get("name", "unknown")
                        if isinstance(tool_call, dict)
                        else getattr(tool_call, "name", "unknown")
                    )
                    tool_args = (
                        tool_call.get("args", {}) if isinstance(tool_call, dict) else getattr(tool_call, "args", {})
                    )
                    content_parts.append(f"  - {tool_name}: {tool_args}")
                content_parts.append("")

        content = "\n".join(content_parts)
        cache_file.write_text(content, encoding="utf-8")

    async def clear_cache(
        self,
        config: RunnableConfig,
    ) -> None:
        """Clear cached development files for the current workflow."""

        metadata = config.get("metadata", {})
        workflow_name = metadata.get("workflow", "")

        workflow_cache_path = self.app.cache_path(f"conversations/{workflow_name}")

        if workflow_cache_path.exists() and workflow_cache_path.is_dir():
            shutil.rmtree(workflow_cache_path)
