from abc import ABC, abstractmethod
from typing import List, Optional

from byte.domain.files.context_manager import FileContext, FileMode


class FileRepositoryInterface(ABC):
    """Repository interface for persisting file context across sessions.

    Abstracts storage mechanism to enable different persistence strategies
    (in-memory, file-based, database) while maintaining consistent API.
    Usage: Implement for specific storage backends like SQLite or JSON files.
    """

    @abstractmethod
    def save(self, file_context: FileContext) -> bool:
        """Persist file context metadata for session restoration.

        Usage: `repository.save(FileContext(path, mode))` -> True if successful
        """
        pass

    @abstractmethod
    def find_by_path(self, path: str) -> Optional[FileContext]:
        """Retrieve file context by path for existence checks.

        Usage: `context = repository.find_by_path("/path/to/file")` -> FileContext or None
        """
        pass

    @abstractmethod
    def all(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """Retrieve all stored contexts, optionally filtered by mode.

        Usage: `all_files = repository.all()` or `editable = repository.all(FileMode.EDITABLE)`
        """
        pass

    @abstractmethod
    def delete_by_path(self, path: str) -> bool:
        """Remove file context from persistent storage.

        Usage: `success = repository.delete_by_path("/path/to/file")` -> True if found and deleted
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored file contexts for clean slate.

        Usage: `repository.clear()` -> empty storage
        """
        pass


class InMemoryFileRepository(FileRepositoryInterface):
    """In-memory implementation of file repository for development and testing.

    Provides fast access without persistence, suitable for temporary sessions
    or when file-based persistence is not desired. Data is lost on restart.
    Usage: `repository = InMemoryFileRepository()` -> temporary storage
    """

    def __init__(self):
        # Use path string as key for fast lookups and duplicate prevention
        self._files = {}

    def save(self, file_context: FileContext) -> bool:
        """Store file context in memory using path as unique key."""
        self._files[str(file_context.path)] = file_context
        return True

    def find_by_path(self, path: str) -> Optional[FileContext]:
        """Retrieve file context by exact path match."""
        return self._files.get(path)

    def all(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """Return all contexts, filtering by mode if specified for UI needs."""
        files = list(self._files.values())
        if mode:
            files = [f for f in files if f.mode == mode]
        return files

    def delete_by_path(self, path: str) -> bool:
        """Remove context if it exists, returning success status for error handling."""
        if path in self._files:
            del self._files[path]
            return True
        return False

    def clear(self) -> None:
        """Clear all stored contexts for fresh start or cleanup."""
        self._files.clear()
