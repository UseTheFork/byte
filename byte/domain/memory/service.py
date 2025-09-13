import uuid
from typing import TYPE_CHECKING, List, Optional

from byte.core.config.configurable import Configurable
from byte.core.events.eventable import Eventable
from byte.domain.memory.checkpointer import ByteCheckpointer

if TYPE_CHECKING:
    from langgraph.checkpoint.sqlite import SqliteSaver

    from byte.container import Container


class MemoryService(Configurable, Eventable):
    """Domain service for managing conversation memory and thread persistence.

    Orchestrates short-term memory through LangGraph checkpointers, providing
    thread management, conversation history, and automatic cleanup. Integrates
    with the agent system to enable stateful conversations.
    Usage: `memory_service.create_thread()` -> new conversation session
    """

    def __init__(self, container: Optional["Container"] = None):
        self.container = container
        self._checkpointer: Optional[ByteCheckpointer] = None
        self._boot_mixins()

    def _boot_mixins(self) -> None:
        """Boot method for auto-initializing mixins."""
        if hasattr(self, "boot_configurable"):
            self.boot_configurable()
        if hasattr(self, "boot_eventable"):
            self.boot_eventable()

    @property
    def checkpointer(self) -> ByteCheckpointer:
        """Get configured checkpointer instance with lazy initialization.

        Usage: `saver = memory_service.checkpointer.get_saver()` -> for graph compilation
        """
        if self._checkpointer is None:
            config_service = self.container.make("config")
            self._checkpointer = ByteCheckpointer(config_service)
        return self._checkpointer

    def get_saver(self) -> "SqliteSaver":
        """Get SqliteSaver for LangGraph graph compilation.

        Usage: `graph = builder.compile(checkpointer=memory_service.get_saver())`
        """
        return self.checkpointer.get_saver()

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

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a specific conversation thread and its history.

        Usage: `success = memory_service.delete_thread(thread_id)` -> cleanup thread
        """
        try:
            saver = self.get_saver()
            saver.delete_thread(thread_id)
            return True
        except Exception:
            return False

    def cleanup_old_threads(self) -> int:
        """Remove old threads based on retention policy.

        Usage: `count = memory_service.cleanup_old_threads()` -> maintenance cleanup
        """
        return self.checkpointer.cleanup_old_threads()
