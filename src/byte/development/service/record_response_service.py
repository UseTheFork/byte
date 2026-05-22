import shutil
from typing import List

from langchain_core.messages import BaseMessage
from langgraph.graph.state import RunnableConfig

from byte.support import Service


class RecordResponseService(Service):
    """Service for recording assistant responses to disk for debugging.

    Writes LLM responses to cache files organized by agent name,
    enabling inspection of prompts and responses during development.
    Usage: `await service.cache_response(result, runtime.context)`
    """

    async def record_response(
        self,
        messages: List[BaseMessage] | None,
        config: RunnableConfig,
    ):
        """Write assistant response to a cache file.

        Creates a cache file named after the agent and writes the response
        content for later inspection during development and debugging.

        Args:
            result: The message result from the assistant
            context: The assistant context containing agent information

        Returns:
            Path to the created cache file

        Usage: `file_path = await service.cache_response(result, runtime.context)`
        """

        if not messages:
            return

        metadata = config.get("metadata", {})
        workflow_name = metadata.get("workflow", "")
        langgraph_node = metadata.get("langgraph_node")
        langgraph_step = metadata.get("langgraph_step")

        cache_file = self.app.cache_path(f"development/{workflow_name}/{langgraph_step}_{langgraph_node}.md")

        # Ensure cache directory exists
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        content_parts = []
        for message in messages:
            message_type = type(message).__name__
            content_parts.append(f"======== {message_type} ========")
            # TODO: The below should check if its a dict and if it is use json dumps to make it pretty etc.
            content_parts.append(str(message.text))
            content_parts.append("")

        content = "\n".join(content_parts)
        cache_file.write_text(content, encoding="utf-8")

    async def clear_development_cache(self) -> None:
        """Clear all files in the development cache directory.

        Removes all cached response files from the development directory
        when the application shuts down to prevent accumulation of debug files.

        Usage: `await service.clear_development_cache()`
        """

        dev_cache_dir = self.app.cache_path("development")

        if dev_cache_dir.exists() and dev_cache_dir.is_dir():
            shutil.rmtree(dev_cache_dir)

    async def clear_cache(
        self,
        config: RunnableConfig,
    ) -> None:
        """ """

        metadata = config.get("metadata", {})
        workflow_name = metadata.get("workflow", "")

        workflow_cache_path = self.app.cache_path(f"development/{workflow_name}")

        if workflow_cache_path.exists() and workflow_cache_path.is_dir():
            shutil.rmtree(workflow_cache_path)
