from typing import List, Optional

from byte.domain.files.context_manager import FileContext, FileContextManager, FileMode
from byte.domain.files.repository import FileRepositoryInterface


class FileService:
    """Domain service for file operations."""

    def __init__(
        self,
        file_repository: FileRepositoryInterface,
        file_context_manager: FileContextManager = None,
    ):
        self.file_repository = file_repository
        self.file_context_manager = file_context_manager or FileContextManager()

    async def add_file(self, path: str, mode: FileMode) -> bool:
        """Add a file to the context."""
        success = self.file_context_manager.add_file(path, mode)

        return success

    async def remove_file(self, path: str) -> bool:
        """Remove a file from the context."""
        success = self.file_context_manager.remove_file(path)

        return success

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """List all files in context."""
        return self.file_context_manager.list_files(mode)

    async def set_file_mode(self, path: str, mode: FileMode) -> bool:
        """Change the mode of a file in context."""
        # Get old mode first
        success = self.file_context_manager.set_file_mode(path, mode)

        return success

    def get_file_context(self, path: str) -> Optional[FileContext]:
        """Get file context by path."""
        return self.file_context_manager.get_file_context(path)

    def generate_context_prompt(self) -> str:
        """Generate a prompt context with all files."""
        return self.file_context_manager.generate_context_prompt()

    def clear_context(self):
        """Clear all files from context."""
        self.file_context_manager.clear()
        # Optionally clear repository
        self.file_repository.clear()

    def load_saved_context(self) -> bool:
        """Load previously saved file context from repository."""
        try:
            saved_files = self.file_repository.all()
            for file_context in saved_files:
                # Re-add to context manager (validates file still exists)
                self.file_context_manager.add_file(
                    str(file_context.path), file_context.mode
                )
            return True
        except Exception:
            return False
