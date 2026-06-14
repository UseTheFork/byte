import fnmatch
import glob
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from byte import Service
from byte.files import FileContext, FileDiscoveryService
from byte.tui import Messages


class FileService(Service):
    """Manage files and project discovery for AI context."""

    def boot(self, **kwargs) -> None:
        """Initialize file service and discovery."""
        self._context_files: Dict[str, FileContext] = {}

    async def notify_file_stats(self) -> None:
        """Notify system of current context file count."""

        count = len(self._context_files)

        self.emit_tui(
            Messages.UpdateFiles(
                count=count,
            ),
        )

    async def add_file(self, path: Union[str, PathLike]) -> bool:
        """Add a file to active context, supporting wildcard patterns."""
        file_discovery = self.app.make(FileDiscoveryService)
        discovered_files = await file_discovery.get_files()
        discovered_file_paths = {str(f.resolve()) for f in discovered_files}

        path_str = str(path)

        # Check if path contains wildcard patterns
        if "*" in path_str or "?" in path_str or "[" in path_str:
            # Handle glob patterns - resolve relative to base path
            if not Path(path_str).is_absolute():
                # Convert relative pattern to absolute by prepending base path
                pattern_path = self.app["path"] / path_str
                matching_paths = glob.glob(str(pattern_path), recursive=True)
            else:
                matching_paths = glob.glob(path_str, recursive=True)

            if not matching_paths:
                return False

            success_count = 0
            for match_path in matching_paths:
                path_obj = Path(match_path).resolve()

                # Only add files that are in the discovery service and are actual files
                if path_obj.is_file() and str(path_obj) in discovered_file_paths:
                    key = str(path_obj)
                    self._context_files[key] = FileContext(path=path_obj, root_path=self.app["path"])
                    success_count += 1

            return success_count > 0
        else:
            # Handle single file path
            if not Path(path).is_absolute():
                # Resolve relative paths from project base path
                path_obj = (self.app["path"] / str(path)).resolve()
            else:
                path_obj = Path(path).resolve()

            # Only add if file is in the discovery service
            if not path_obj.is_file() or str(path_obj) not in discovered_file_paths:
                return False

            key = str(path_obj)

            # If the file is already in context, return False
            if key in self._context_files:
                return False

            self._context_files[key] = FileContext(path=path_obj, root_path=self.app["path"])

            # Emit event for UI updates and other interested components
            return True

    async def remove_file(self, path: Union[str, PathLike]) -> bool:
        """Remove a file from active context, supporting wildcard patterns."""
        file_discovery = self.app.make(FileDiscoveryService)
        discovered_files = await file_discovery.get_files()
        discovered_file_paths = {str(f.resolve()) for f in discovered_files}

        path_str = str(path)

        # Check if path contains wildcard patterns
        if "*" in path_str or "?" in path_str or "[" in path_str:
            # Handle glob patterns - match against files currently in context
            matching_paths = []
            for context_path in list(self._context_files.keys()):
                # Only consider files that are in the discovery service
                if context_path not in discovered_file_paths:
                    continue

                # Convert absolute path back to relative for pattern matching
                try:
                    relative_path = str(Path(context_path).relative_to(self.app["path"]))
                    if fnmatch.fnmatch(relative_path, path_str) or fnmatch.fnmatch(context_path, path_str):
                        matching_paths.append(context_path)
                except ValueError:
                    # If can't make relative, try matching absolute path
                    if fnmatch.fnmatch(context_path, path_str):
                        matching_paths.append(context_path)

            if not matching_paths:
                return False

            # Remove all matching files
            for match_path in matching_paths:
                del self._context_files[match_path]
                # await self.event(FileRemoved(file_path=match_path))

            return True
        else:
            # Handle single file path
            if not Path(path).is_absolute():
                # Resolve relative paths from project base path
                path_obj = (self.app["path"] / str(path)).resolve()
            else:
                path_obj = Path(path).resolve()
            key = str(path_obj)

            # Only remove if file is in context
            if key in self._context_files:
                del self._context_files[key]
                # await self.event(FileRemoved(file_path=str(path_obj)))
                return True
            return False

    def list_files(self) -> List[FileContext]:
        """List all files in context sorted by relative path."""
        files = list(self._context_files.values())

        # Sort by relative path for consistent, user-friendly ordering
        return sorted(files, key=lambda f: f.relative_path)

    def get_file_context(self, path: Union[str, PathLike]) -> Optional[FileContext]:
        """Retrieve file context metadata for a specific path."""
        path_obj = Path(path).resolve()
        return self._context_files.get(str(path_obj))

    async def generate_context_prompt(self) -> list[str]:
        """Generate formatted file strings for prompt context."""
        files = []

        if not self._context_files:
            return files

        for file_ctx in sorted(self._context_files.values(), key=lambda f: f.relative_path):
            files.append(file_ctx.to_boundary())

        return files

    async def clear_context(self) -> None:
        """Clear all files from context for fresh start."""
        self._context_files.clear()

    # Project file discovery methods
    async def get_project_files(self, extension: Optional[str] = None) -> List[str]:
        """Get all project files as relative path strings, optionally filtered by extension."""
        file_discovery = self.app.make(FileDiscoveryService)
        return await file_discovery.get_relative_paths(extension)

    async def find_project_files(self, pattern: str) -> List[str]:
        """Find project files matching a pattern for completions."""
        file_discovery = self.app.make(FileDiscoveryService)
        matches = await file_discovery.find_files(pattern)

        if not self.app["path"]:
            return [str(f) for f in matches]
        return [str(f.relative_to(self.app["path"])) for f in matches]

    async def is_file_in_context(self, path: Union[str, PathLike]) -> bool:
        """Check if a file is currently in the AI context."""
        path_obj = Path(path).resolve()
        return str(path_obj) in self._context_files
