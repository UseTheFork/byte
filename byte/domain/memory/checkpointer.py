from typing import TYPE_CHECKING, Optional

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from byte.domain.memory.config import MemoryConfig

if TYPE_CHECKING:
    pass


class ByteCheckpointer:
    """Wrapper for LangGraph checkpointer with Byte-specific configuration.

    Manages async SQLite-based conversation persistence with automatic database
    setup and configuration integration. Provides async access to conversation
    history and state management for streaming agent operations.
    Usage: `checkpointer = ByteCheckpointer(config_service).get_saver()`
    """

    def __init__(self, config: MemoryConfig):
        self._saver: Optional[AsyncSqliteSaver] = None
        self._config = config

    async def get_saver(self) -> AsyncSqliteSaver:
        """Get configured AsyncSqliteSaver instance with lazy initialization.

        Usage: `saver = await checkpointer.get_saver()` -> ready for graph compilation
        """
        if self._saver is None:
            self._saver = await self._create_saver()
        return self._saver

    async def _create_saver(self) -> AsyncSqliteSaver:
        """Create and configure AsyncSqliteSaver with Byte-specific settings."""
        # Get database path from config or use default
        db_path = self._config.database_path

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create async SQLite connection
        conn = await aiosqlite.connect(str(db_path))

        # Create and setup the async saver
        saver = AsyncSqliteSaver(conn)
        await saver.setup()  # Initialize database schema

        return saver

    async def cleanup_old_threads(self) -> int:
        """Remove old conversation threads based on retention policy.

        Usage: `count = await checkpointer.cleanup_old_threads()` -> returns deleted count
        """
        if self._saver is None:
            return 0

        # memory_config = self.config_service.config.memory
        # TODO: Implementation would query and delete old threads
        # This is a placeholder for the actual cleanup logic
        return 0

    async def close(self):
        """Close database connection."""
        if self._saver and hasattr(self._saver, "conn") and self._saver.conn:
            await self._saver.conn.close()
            self._saver = None
