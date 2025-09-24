from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.base import RunnableSerializable

from byte.domain.agent.base import Agent
from byte.domain.agent.coder.prompts import coder_prompt
from byte.domain.cli_input.tools import user_confirm
from byte.domain.files.service.file_service import FileService
from byte.domain.llm.service.llm_service import LLMService


class CoderAgent(Agent):
    """Domain service for the coder agent specialized in software development.

    Pure domain service that handles coding logic without UI concerns.
    Integrates with file context, memory, and development tools through
    the actor system for clean separation of concerns.
    """

    name: str = "coder"

    def get_tools(self):
        """Return tools available to the coder agent."""
        return [user_confirm]
        # return [user_confirm, user_select, user_input, replace_text_in_file]

    async def build(self) -> RunnableSerializable:
        """Build and compile the coder agent graph with memory and tools."""

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()

        # Create the assistant runnable
        assistant_runnable = coder_prompt | llm.bind_tools(self.get_tools())

        return assistant_runnable

    async def _get_file_context(self, state) -> dict:
        """Fetch current file context for the agent."""

        file_service: FileService = await self.make(FileService)
        file_context = file_service.generate_context_prompt()
        return {"file_context": file_context}
