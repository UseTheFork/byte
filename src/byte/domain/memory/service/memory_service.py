import uuid
from typing import Optional

from langgraph.checkpoint.memory import InMemorySaver

from byte.core.service.base_service import Service


class MemoryService(Service):
    """Domain service for managing conversation memory and thread persistence.

    Orchestrates short-term memory through LangGraph checkpointers, providing
    thread management, conversation history, and automatic cleanup. Integrates
    with the agent system to enable stateful conversations.
    Usage: `memory_service.create_thread()` -> new conversation session
    """

    _checkpointer: Optional[InMemorySaver] = None
    _current_thread_id: Optional[str] = None

    async def get_checkpointer(self) -> InMemorySaver:
        """Get configured checkpointer instance with lazy initialization.

        Usage: `checkpointer = await memory_service.get_checkpointer()` -> for accessing checkpointer
        """
        if self._checkpointer is None:
            self._checkpointer = InMemorySaver()
        return self._checkpointer

    async def get_saver(self) -> InMemorySaver:
        """Get InMemorySaver for LangGraph graph compilation.

        Usage: `graph = builder.compile(checkpointer=await memory_service.get_saver())`
        """
        checkpointer = await self.get_checkpointer()
        return checkpointer

    def create_thread(self) -> str:
        """Create a new conversation thread with unique identifier.

        Usage: `thread_id = memory_service.create_thread()` -> new conversation
        """
        return str(uuid.uuid4())

    async def set_current_thread(self, thread_id: str) -> None:
        """Set the active thread for the current session.

        Usage: `await memory_service.set_current_thread(thread_id)` -> sets active thread
        """
        self._current_thread_id = thread_id

    def get_current_thread(self) -> Optional[str]:
        """Get the currently active thread ID.

        Usage: `thread_id = memory_service.get_current_thread()` -> current active thread
        """
        return self._current_thread_id

    async def get_or_create_thread(self) -> str:
        """Get current thread or create a new one if none exists.

        Usage: `thread_id = await memory_service.get_or_create_thread()` -> ensures thread exists
        """
        if self._current_thread_id is None:
            self._current_thread_id = self.create_thread()
            # await self._persist_current_thread(self._current_thread_id)
        return self._current_thread_id

    async def new_thread(self) -> str:
        """Create a new conversation thread and set it as the current active thread.

        Generates a new unique thread identifier, sets it as the current thread,
        and returns the ID for immediate use in conversation flows.

        Usage: `thread_id = await memory_service.new_thread()` -> starts fresh conversation
        """
        thread_id = self.create_thread()
        await self.set_current_thread(thread_id)
        return thread_id
