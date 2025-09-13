import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from langgraph.checkpoint.sqlite import SqliteSaver

if TYPE_CHECKING:
    from byte.core.config.service import ConfigService


class ByteCheckpointer:
    """Wrapper for LangGraph checkpointer with Byte-specific configuration.

    Manages SQLite-based conversation persistence with automatic database
    setup and configuration integration. Provides thread-safe access to
    conversation history and state management.
    Usage: `checkpointer = ByteCheckpointer(config_service).get_saver()`
    """

    def __init__(self, config_service: "ConfigService"):
        self.config_service = config_service
        self._saver: Optional[SqliteSaver] = None

    def get_saver(self) -> SqliteSaver:
        """Get configured SqliteSaver instance with lazy initialization.

        Usage: `saver = checkpointer.get_saver()` -> ready for graph compilation
        """
        if self._saver is None:
            self._saver = self._create_saver()
        return self._saver

    def _create_saver(self) -> SqliteSaver:
        """Create and configure SqliteSaver with Byte-specific settings."""
        # Get database path from config or use default
        memory_config = self.config_service.config.memory
        if memory_config.database_path:
            db_path = Path(memory_config.database_path)
        else:
            db_path = self.config_service.byte_dir / "memory.db"

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create SQLite connection with thread safety
        conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,  # Allow multi-thread access
            timeout=30.0,  # 30 second timeout for busy database
        )

        # Create and setup the saver
        saver = SqliteSaver(conn)
        saver.setup()  # Initialize database schema

        return saver

    def cleanup_old_threads(self) -> int:
        """Remove old conversation threads based on retention policy.

        Usage: `count = checkpointer.cleanup_old_threads()` -> returns deleted count
        """
        if self._saver is None:
            return 0

        # memory_config = self.config_service.config.memory
        # Implementation would query and delete old threads
        # This is a placeholder for the actual cleanup logic
        return 0
