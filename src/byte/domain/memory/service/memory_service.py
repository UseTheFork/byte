import uuid
from typing import TYPE_CHECKING, List, Optional

from byte.core.service.base_service import Service
from byte.domain.memory.checkpointer import ByteCheckpointer
from byte.domain.memory.config import MemoryConfig

if TYPE_CHECKING:
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class MemoryService(Service):
    """Domain service for managing conversation memory and thread persistence.

    Orchestrates short-term memory through LangGraph checkpointers, providing
    thread management, conversation history, and automatic cleanup. Integrates
    with the agent system to enable stateful conversations.
    Usage: `memory_service.create_thread()` -> new conversation session
    """

    _checkpointer: Optional[ByteCheckpointer] = None
    _service_config: MemoryConfig
    _current_thread_id: Optional[str] = None

    async def _configure_service(self) -> None:
        """Configure memory service with database path and retention settings."""

        self._service_config = MemoryConfig(
            database_path=self._config.byte_dir / "memory.db"
        )

    async def get_checkpointer(self) -> ByteCheckpointer:
        """Get configured checkpointer instance with lazy initialization.

        Usage: `checkpointer = await memory_service.get_checkpointer()` -> for accessing checkpointer
        """
        if self._checkpointer is None:
            self._checkpointer = ByteCheckpointer(self._service_config)
        return self._checkpointer

    async def get_saver(self) -> "AsyncSqliteSaver":
        """Get AsyncSqliteSaver for LangGraph graph compilation.

        Usage: `graph = builder.compile(checkpointer=await memory_service.get_saver())`
        """
        checkpointer = await self.get_checkpointer()
        return await checkpointer.get_saver()

    def create_thread(self) -> str:
        """Create a new conversation thread with unique identifier.

        Usage: `thread_id = memory_service.create_thread()` -> new conversation
        """
        return str(uuid.uuid4())

    def list_threads(self, limit: int = 50) -> List[str]:
        """List recent conversation threads.

        Usage: `threads = memory_service.list_threads()` -> recent thread IDs
        """
        # This would query the checkpointer database for thread IDs
        # Placeholder implementation
        return []

    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a specific conversation thread and its history.

        Usage: `success = await memory_service.delete_thread(thread_id)` -> cleanup thread
        """
        try:
            saver = await self.get_saver()
            await saver.adelete_thread(thread_id)
            return True
        except Exception:
            return False

    async def cleanup_old_threads(self) -> int:
        """Remove old threads based on retention policy.

        Usage: `count = await memory_service.cleanup_old_threads()` -> maintenance cleanup
        """
        checkpointer = await self.get_checkpointer()
        return await checkpointer.cleanup_old_threads()

    async def close(self):
        """Close memory service resources."""
        if self._checkpointer:
            await self._checkpointer.close()

    async def set_current_thread(self, thread_id: str) -> None:
        """Set the active thread for the current session.

        Usage: `await memory_service.set_current_thread(thread_id)` -> sets active thread
        """
        self._current_thread_id = thread_id
        # Optionally persist to config or database
        # await self._persist_current_thread(thread_id)

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
