from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class FileMode(Enum):
    READ_ONLY = "read_only"
    EDITABLE = "editable"


@dataclass
class FileContext:
    path: Path
    mode: FileMode

    @property
    def relative_path(self) -> str:
        """Get relative path from current working directory."""
        try:
            return str(self.path.relative_to(Path.cwd()))
        except ValueError:
            return str(self.path)

    def get_content(self) -> Optional[str]:
        """Read file content from disk."""
        try:
            return self.path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None


class FileContextManager:
    def __init__(self):
        self._files: Dict[str, FileContext] = {}

    def add_file(self, file_path: str, mode: FileMode = FileMode.READ_ONLY) -> bool:
        """Add a file to the context."""
        path = Path(file_path).resolve()

        if not path.exists():
            return False

        if not path.is_file():
            return False

        key = str(path)
        self._files[key] = FileContext(path=path, mode=mode)
        return True

    def remove_file(self, file_path: str) -> bool:
        """Remove a file from the context."""
        path = Path(file_path).resolve()
        key = str(path)

        if key in self._files:
            del self._files[key]
            return True
        return False

    def set_file_mode(self, file_path: str, mode: FileMode) -> bool:
        """Change the mode of a file in the context."""
        path = Path(file_path).resolve()
        key = str(path)

        if key in self._files:
            self._files[key].mode = mode
            return True
        return False

    def get_file_context(self, file_path: str) -> Optional[FileContext]:
        """Get file context by path."""
        path = Path(file_path).resolve()
        return self._files.get(str(path))

    def list_files(self, mode: Optional[FileMode] = None) -> List[FileContext]:
        """List all files, optionally filtered by mode."""
        files = list(self._files.values())

        if mode is not None:
            files = [f for f in files if f.mode == mode]

        return sorted(files, key=lambda f: f.relative_path)

    def generate_context_prompt(self) -> str:
        """Generate a prompt context with all files."""
        if not self._files:
            return ""

        context = "Here are the files in the current context:\n\n"

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
        """Clear all files from context."""
        self._files.clear()


# Global file context manager
file_context_manager = FileContextManager()
