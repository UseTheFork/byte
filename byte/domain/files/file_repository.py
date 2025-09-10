from abc import ABC, abstractmethod
from typing import List, Optional

from byte.domain.files.context_manager import FileContext, FileMode


class FileRepositoryInterface(ABC):
    @abstractmethod
    def save(self, file_context: FileContext) -> bool:
        pass

    @abstractmethod
    def find_by_path(self, path: str) -> Optional[FileContext]:
        pass

    @abstractmethod
    def all(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        pass

    @abstractmethod
    def delete_by_path(self, path: str) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class InMemoryFileRepository(FileRepositoryInterface):
    def __init__(self):
        self._files = {}

    def save(self, file_context: FileContext) -> bool:
        self._files[str(file_context.path)] = file_context
        return True

    def find_by_path(self, path: str) -> Optional[FileContext]:
        return self._files.get(path)

    def all(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        files = list(self._files.values())
        if mode:
            files = [f for f in files if f.mode == mode]
        return files

    def delete_by_path(self, path: str) -> bool:
        if path in self._files:
            del self._files[path]
            return True
        return False

    def clear(self) -> None:
        self._files.clear()
