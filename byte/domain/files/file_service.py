from typing import List, Optional

from byte.repositories.file_repository import FileRepositoryInterface

from .context_manager import FileContext, FileContextManager, FileMode


class FileService:
    """Domain service for file operations."""

    def __init__(
        self,
        file_repository: FileRepositoryInterface,
        file_context_manager: FileContextManager = None,
    ):
        self.file_repository = file_repository
        self.file_context_manager = file_context_manager or FileContextManager()

    def add_file(self, path: str, mode: FileMode) -> bool:
        """Add a file to the context."""
        success = self.file_context_manager.add_file(path, mode)
        if success:
            # Optionally persist to repository
            file_context = self.file_context_manager.get_file_context(path)
            if file_context:
                self.file_repository.save(file_context)
        return success

    def remove_file(self, path: str) -> bool:
        """Remove a file from the context."""
        success = self.file_context_manager.remove_file(path)
        if success:
            # Optionally remove from repository
            self.file_repository.delete_by_path(path)
        return success

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """List all files in context."""
        return self.file_context_manager.list_files(mode)

    def set_file_mode(self, path: str, mode: FileMode) -> bool:
        """Change the mode of a file in context."""
        success = self.file_context_manager.set_file_mode(path, mode)
        if success:
            # Update in repository
            file_context = self.file_context_manager.get_file_context(path)
            if file_context:
                self.file_repository.save(file_context)
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
from typing import List, Optional
from .context_manager import FileContext, FileMode, FileContextManager


class FileService:
    def __init__(self, repository, context_manager: FileContextManager):
        self.repository = repository
        self.context_manager = context_manager

    def add_file(self, path: str, mode: FileMode) -> bool:
        if self.context_manager.add_file(path, mode):
            # Optionally save to repository
            file_context = self.context_manager._files.get(path)
            if file_context:
                self.repository.save(file_context)
            return True
        return False

    def remove_file(self, path: str) -> bool:
        if self.context_manager.remove_file(path):
            self.repository.delete_by_path(path)
            return True
        return False

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        return self.context_manager.list_files(mode)
