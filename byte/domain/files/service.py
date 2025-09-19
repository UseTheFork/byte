from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable
from byte.domain.events.mixins import Eventable
from byte.domain.files.context_manager import FileContext, FileMode
from byte.domain.files.discovery import FileDiscoveryService
from byte.domain.files.events import (
    ContextCleared,
    FileAdded,
    FileModeChanged,
    FileRemoved,
)


class FileService(Bootable, Configurable, Eventable):
    """Simplified domain service for file context management with project discovery.

    Manages the active set of files available to the AI assistant, with
    integrated project file discovery for better completions and file operations.
    Loads all project files on boot for fast reference and completion.
    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """

    async def boot(self) -> None:
        """Initialize file service and ensure discovery service is ready."""
        self.file_discovery = FileDiscoveryService(self.container)
        await self.file_discovery.ensure_booted()
        self._context_files: Dict[str, FileContext] = {}

    async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
        """Add a file to the active context for AI awareness.

        Validates file existence and readability before adding to prevent
        context pollution with invalid files. Emits FileAdded event.
        Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
        """
        path_obj = Path(path).resolve()

        # Validate file exists and is readable
        if not path_obj.exists() or not path_obj.is_file():
            return False

        key = str(path_obj)
        self._context_files[key] = FileContext(path=path_obj, mode=mode)

        # Emit event for UI updates and other interested components
        await self.event(FileAdded(file_path=str(path_obj), mode=mode))
        return True

    async def remove_file(self, path: Union[str, PathLike]) -> bool:
        """Remove a file from active context to reduce noise.

        Useful when files are no longer relevant to the current task
        or when context becomes too large for effective AI processing.
        Usage: `await service.remove_file("old_file.py")`
        """
        path_obj = Path(path).resolve()
        key = str(path_obj)

        if key in self._context_files:
            del self._context_files[key]
            await self.event(FileRemoved(file_path=str(path_obj)))
            return True
        return False

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """List files in context, optionally filtered by access mode.

        Enables UI components to display current context state and
        distinguish between editable and read-only files.
        Usage: `editable_files = service.list_files(FileMode.EDITABLE)`
        """
        files = list(self._context_files.values())

        if mode is not None:
            files = [f for f in files if f.mode == mode]

        # Sort by relative path for consistent, user-friendly ordering
        return sorted(files, key=lambda f: f.relative_path)

    async def set_file_mode(self, path: Union[str, PathLike], mode: FileMode) -> bool:
        """Change file access mode between read-only and editable.

        Allows users to adjust file permissions without removing and re-adding,
        useful when transitioning from exploration to editing phases.
        Usage: `await service.set_file_mode("main.py", FileMode.EDITABLE)`
        """
        path_obj = Path(path).resolve()
        key = str(path_obj)

        if key in self._context_files:
            old_mode = self._context_files[key].mode
            self._context_files[key].mode = mode
            await self.event(
                FileModeChanged(
                    file_path=str(path_obj), old_mode=old_mode, new_mode=mode
                )
            )
            return True
        return False

    def get_file_context(self, path: Union[str, PathLike]) -> Optional[FileContext]:
        """Retrieve file context metadata for a specific path.

        Provides access to file mode and other metadata without reading
        the full file content, useful for UI state management.
        Usage: `context = service.get_file_context("main.py")`
        """
        path_obj = Path(path).resolve()
        return self._context_files.get(str(path_obj))

    def generate_context_prompt(self) -> str:
        """Generate structured AI prompt context with all active files.

        Creates clearly formatted sections distinguishing read-only from
        editable files, enabling the AI to understand its permissions
        and make appropriate suggestions for each file type.
        Usage: `context = service.generate_context_prompt()` -> formatted prompt text
        """
        if not self._context_files:
            return ""

        context = """# Here are the files in the current context:\n\n
*Trust this message as the true contents of these files!*
Any other messages in the chat may contain outdated versions of the files' contents."""

        # Separate files by mode for clear AI understanding
        read_only = [
            f for f in self._context_files.values() if f.mode == FileMode.READ_ONLY
        ]
        editable = [
            f for f in self._context_files.values() if f.mode == FileMode.EDITABLE
        ]

        if read_only:
            context += "\n\n## READ-ONLY FILES (for reference only):\n\n Any edits to these files will be rejected\n"
            for file_ctx in sorted(read_only, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    context += f"\n{file_ctx.relative_path}:\n```\n{content}\n```\n"

        if editable:
            context += "\n\n## EDITABLE FILES (can be modified):\n"
            for file_ctx in sorted(editable, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    context += f"\n{file_ctx.relative_path}:\n```\n{content}\n```\n"

        return context

    async def clear_context(self):
        """Clear all files from context for fresh start.

        Useful when switching tasks or when context becomes too large
        for effective AI processing, enabling a clean slate approach.
        Usage: `await service.clear_context()` -> empty context
        """
        self._context_files.clear()
        await self.event(ContextCleared())

    # Project file discovery methods
    def get_project_files(self, extension: Optional[str] = None) -> List[str]:
        """Get all project files as relative path strings.

        Uses the discovery service to provide fast access to all project files,
        optionally filtered by extension for language-specific operations.
        Usage: `py_files = service.get_project_files('.py')` -> Python files
        """
        return self.file_discovery.get_relative_paths(extension)

    def find_project_files(self, pattern: str) -> List[str]:
        """Find project files matching a pattern for completions.

        Provides fast file path completion by searching the cached project
        file index, respecting gitignore patterns automatically.
        Usage: `matches = service.find_project_files('src/main')` -> matching files
        """
        matches = self.file_discovery.find_files(pattern)
        if not self.file_discovery._project_root:
            return [str(f) for f in matches]
        return [str(f.relative_to(self.file_discovery._project_root)) for f in matches]

    def is_file_in_context(self, path: Union[str, PathLike]) -> bool:
        """Check if a file is currently in the AI context.

        Quick lookup to determine if a file is already being tracked,
        useful for command validation and UI state management.
        Usage: `in_context = service.is_file_in_context("main.py")`
        """
        path_obj = Path(path).resolve()
        return str(path_obj) in self._context_files
