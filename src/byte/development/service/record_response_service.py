from datetime import datetime

from langchain_core.runnables import Runnable
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

from byte.agent import AssistantContextSchema
from byte.support import Service


class RecordResponseService(Service):
    """Service for recording assistant responses to disk for debugging.

    Writes LLM responses to cache files organized by agent name,
    enabling inspection of prompts and responses during development.
    Usage: `await service.cache_response(result, runtime.context)`
    """

    async def record_response(
        self,
        agent_state,
        runnable: Runnable,
        runtime: Runtime[AssistantContextSchema],
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
        if not self.app.is_development():
            return None

        agent_name = runtime.context.agent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_file = self.app.cache_path(f"development/{agent_name}_{timestamp}.md")

        # Ensure cache directory exists
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        template = runnable.get_prompts(config)
        prompt_value = await template[0].ainvoke(agent_state)

        messages = prompt_value.to_messages()

        content_parts = []
        for message in messages:
            message_type = type(message).__name__
            content_parts.append(f"======== {message_type} ========")
            content_parts.append(str(message.content))
            content_parts.append("")

        content = "\n".join(content_parts)
        cache_file.write_text(content, encoding="utf-8")

    async def clear_development_cache(self) -> None:
        """Clear all files in the development cache directory.

        Removes all cached response files from the development directory
        when the application shuts down to prevent accumulation of debug files.

        Usage: `await service.clear_development_cache()`
        """
        import shutil

        dev_cache_dir = self.app.cache_path("development")

        if dev_cache_dir.exists() and dev_cache_dir.is_dir():
            shutil.rmtree(dev_cache_dir)
