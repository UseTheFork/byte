from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union


class FileMode(Enum):
    """File access modes defining AI interaction permissions.

    READ_ONLY: AI can reference but not modify the file content
    EDITABLE: AI can propose changes via SEARCH/REPLACE blocks
    """

    READ_ONLY = "read_only"
    EDITABLE = "editable"


@dataclass(frozen=True)
class FileContext:
    """Metadata container for files in the AI context.

    Tracks file location and access permissions while providing
    utilities for path display and content access.
    Usage: `FileContext(Path("main.py"), FileMode.EDITABLE)`
    """

    path: Path
    mode: FileMode

    @property
    def relative_path(self) -> str:
        """Get user-friendly relative path for display purposes.

        Prefers relative paths for cleaner UI display, falling back
        to absolute paths when files are outside the working directory.
        Usage: `file_ctx.relative_path` -> "src/main.py" instead of "/full/path/src/main.py"
        """
        try:
            return str(self.path.relative_to(Path.cwd()))
        except ValueError:
            return str(self.path)

    def get_content(self) -> Optional[str]:
        """Read file content from disk with error handling.

        Gracefully handles file system errors and encoding issues
        to prevent context generation failures from problematic files.
        Usage: `content = file_ctx.get_content()` -> file content or None if error
        """
        try:
            return self.path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            return None


class FileContextManager:
    """Manages the active set of files available to the AI assistant.

    Maintains in-memory state of files the AI should be aware of,
    handling validation, deduplication, and context generation for
    optimal AI prompt construction.
    Usage: `manager.add_file("main.py", FileMode.EDITABLE)`
    """

    def __init__(self):
        # Use absolute path strings as keys to prevent duplicates
        self._files: Dict[str, FileContext] = {}

    def add_file(
        self, file_path: Union[str, PathLike], mode: FileMode = FileMode.READ_ONLY
    ) -> bool:
        """Add a file to the active context with validation.

        Resolves paths to absolute form to prevent duplicates and
        validates file existence to maintain context integrity.
        Usage: `success = manager.add_file("config.py", FileMode.READ_ONLY)`
        """
        path = Path(file_path).resolve()

        # Validate file exists to prevent broken context
        if not path.exists():
            return False

        # Only accept regular files, not directories or special files
        if not path.is_file():
            return False

        key = str(path)
        self._files[key] = FileContext(path=path, mode=mode)
        return True

    def remove_file(self, file_path: Union[str, PathLike]) -> bool:
        """Remove a file from active context to reduce noise.

        Resolves path to match the key format used during addition
        to ensure reliable removal regardless of path format.
        Usage: `success = manager.remove_file("./config.py")`
        """
        path = Path(file_path).resolve()
        key = str(path)

        if key in self._files:
            del self._files[key]
            return True
        return False

    def set_file_mode(self, file_path: Union[str, PathLike], mode: FileMode) -> bool:
        """Change file access permissions without removing from context.

        Allows transitioning between read-only and editable modes
        as user needs change during development workflow.
        Usage: `success = manager.set_file_mode("main.py", FileMode.EDITABLE)`
        """
        path = Path(file_path).resolve()
        key = str(path)

        if key in self._files:
            self._files[key].mode = mode
            return True
        return False

    def get_file_context(
        self, file_path: Union[str, PathLike]
    ) -> Optional[FileContext]:
        """Retrieve file metadata for UI state management.

        Provides access to file mode and path information without
        reading content, useful for command completion and status display.
        Usage: `context = manager.get_file_context("main.py")`
        """
        path = Path(file_path).resolve()
        return self._files.get(str(path))

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """List files in context, optionally filtered by access mode.

        Enables UI components to display different file categories
        and supports command completion with relevant file subsets.
        Usage: `editable = manager.list_files(FileMode.EDITABLE)`
        """
        files = list(self._files.values())

        if mode is not None:
            files = [f for f in files if f.mode == mode]

        # Sort by relative path for consistent, user-friendly ordering
        return sorted(files, key=lambda f: f.relative_path)

    def generate_context_prompt(self) -> str:
        """Generate structured AI prompt context with all active files.

        Creates clearly formatted sections distinguishing read-only from
        editable files, enabling the AI to understand its permissions
        and make appropriate suggestions for each file type.
        Usage: `context = manager.generate_context_prompt()` -> formatted prompt text
        """
        if not self._files:
            return ""

        context = "Here are the files in the current context:\n\n"

        # Separate files by mode for clear AI understanding
        read_only = [f for f in self._files.values() if f.mode == FileMode.READ_ONLY]
        editable = [f for f in self._files.values() if f.mode == FileMode.EDITABLE]

        if read_only:
            context += "READ-ONLY FILES (for reference only):\n"
            for file_ctx in sorted(read_only, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    context += f"\n{file_ctx.relative_path}:\n```\n{content}\n```\n"
                else:
                    context += f"\n{file_ctx.relative_path}: [Error reading file]\n"

        if editable:
            context += "\nEDITABLE FILES (can be modified):\n"
            for file_ctx in sorted(editable, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    context += f"\n{file_ctx.relative_path}:\n```\n{content}\n```\n"
                else:
                    context += f"\n{file_ctx.relative_path}: [Error reading file]\n"

        return context

    def clear(self):
        """Clear all files from context for fresh start.

        Useful when switching tasks or when context becomes too large
        for effective AI processing, enabling a clean slate approach.
        Usage: `manager.clear()` -> empty context
        """
        self._files.clear()
