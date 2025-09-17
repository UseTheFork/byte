import uuid
from typing import TYPE_CHECKING, List, Optional

from byte.core.config.mixins import Configurable
from byte.core.events.eventable import Eventable
from byte.core.service.mixins import Bootable
from byte.domain.memory.checkpointer import ByteCheckpointer
from byte.domain.memory.config import MemoryConfig

if TYPE_CHECKING:
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class MemoryService(Bootable, Configurable, Eventable):
    """Domain service for managing conversation memory and thread persistence.

    Orchestrates short-term memory through LangGraph checkpointers, providing
    thread management, conversation history, and automatic cleanup. Integrates
    with the agent system to enable stateful conversations.
    Usage: `memory_service.create_thread()` -> new conversation session
    """

    _checkpointer: Optional[ByteCheckpointer] = None
    _service_config: MemoryConfig

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
