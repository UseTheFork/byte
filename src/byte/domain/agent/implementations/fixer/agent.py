from langchain_core.language_models.chat_models import BaseChatModel

from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.fixer.prompts import fixer_prompt
from byte.domain.llm.service.llm_service import LLMService


class FixerAgent(CoderAgent):
    """"""

    async def get_checkpointer(self):
        return False

    def get_tools(self):
        """Return tools available to the coder agent."""
        return []

    async def get_assistant_runnable(self):
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()

        # Create the assistant runnable with out any tools. So regardless it wont make a tool call even thou we have a tool node.
        return fixer_prompt | llm
