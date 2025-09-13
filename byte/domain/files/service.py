from os import PathLike
from typing import List, Optional, Union

from byte.domain.files.context_manager import FileContext, FileContextManager, FileMode
from byte.domain.files.repository import FileRepositoryInterface


class FileService:
    """Domain service orchestrating file operations and context management.

    Coordinates between the context manager (in-memory state) and repository
    (persistence) to provide a unified interface for file operations. Enables
    the AI assistant to maintain awareness of relevant files across sessions.
    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """

    def __init__(
        self,
        file_repository: FileRepositoryInterface,
        file_context_manager: FileContextManager | None = None,
    ):
        # Repository handles persistence while context manager handles active state
        self.file_repository = file_repository
        self.file_context_manager = file_context_manager or FileContextManager()

    async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
        """Add a file to the active context for AI awareness.

        Validates file existence and readability before adding to prevent
        context pollution with invalid files.
        Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
        """
        success = self.file_context_manager.add_file(path, mode)

        return success

    async def remove_file(self, path: Union[str, PathLike]) -> bool:
        """Remove a file from active context to reduce noise.

        Useful when files are no longer relevant to the current task
        or when context becomes too large for effective AI processing.
        Usage: `await service.remove_file("old_file.py")`
        """
        success = self.file_context_manager.remove_file(path)

        return success

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """List files in context, optionally filtered by access mode.

        Enables UI components to display current context state and
        distinguish between editable and read-only files.
        Usage: `editable_files = service.list_files(FileMode.EDITABLE)`
        """
        return self.file_context_manager.list_files(mode)

    async def set_file_mode(self, path: Union[str, PathLike], mode: FileMode) -> bool:
        """Change file access mode between read-only and editable.

        Allows users to adjust file permissions without removing and re-adding,
        useful when transitioning from exploration to editing phases.
        Usage: `await service.set_file_mode("main.py", FileMode.EDITABLE)`
        """
        success = self.file_context_manager.set_file_mode(path, mode)

        return success

    def get_file_context(self, path: Union[str, PathLike]) -> Optional[FileContext]:
        """Retrieve file context metadata for a specific path.

        Provides access to file mode and other metadata without reading
        the full file content, useful for UI state management.
        Usage: `context = service.get_file_context("main.py")`
        """
        return self.file_context_manager.get_file_context(path)

    def generate_context_prompt(self) -> str:
        """Generate formatted context for AI prompt inclusion.

        Creates a structured prompt containing all active files with clear
        mode distinctions, enabling the AI to understand what it can modify.
        Usage: `context = service.generate_context_prompt()` -> includes in AI prompt
        """
        return self.file_context_manager.generate_context_prompt()

    def clear_context(self):
        """Clear all files from active context and optionally from persistence.

        Useful for starting fresh on a new task or when context becomes
        too cluttered to be effective for AI processing.
        Usage: `service.clear_context()` -> clean slate
        """
        self.file_context_manager.clear()
        # Clear repository to prevent stale data on reload
        self.file_repository.clear()

    def load_saved_context(self) -> bool:
        """Restore previously saved file context from persistent storage.

        Validates that saved files still exist and are readable before
        adding to context, gracefully handling deleted or moved files.
        Usage: `success = service.load_saved_context()` -> restore session state
        """
        try:
            saved_files = self.file_repository.all()
            for file_context in saved_files:
                # Re-validate file existence to handle filesystem changes
                self.file_context_manager.add_file(
                    str(file_context.path), file_context.mode
                )
            return True
        except (FileNotFoundError, PermissionError, OSError):
            return False
