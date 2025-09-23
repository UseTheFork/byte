import glob
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.service.base_service import Service
from byte.domain.files.context_manager import FileContext, FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService


class FileService(Service):
    """Simplified domain service for file context management with project discovery.

    Manages the active set of files available to the AI assistant, with
    integrated project file discovery for better completions and file operations.
    Loads all project files on boot for fast reference and completion.
    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """

    async def boot(self) -> None:
        """Initialize file service and ensure discovery service is ready."""
        self._context_files: Dict[str, FileContext] = {}

    async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
        """Add a file to the active context for AI awareness.

        Supports wildcard patterns like 'byte/*' to add multiple files at once.
        Only adds files that are available in the FileDiscoveryService to ensure
        they are valid project files that respect gitignore patterns.
        Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
        Usage: `await service.add_file("src/*.py", FileMode.EDITABLE)` -> adds all Python files
        """
        console = await self.make(Console)
        file_discovery = await self.make(FileDiscoveryService)
        discovered_files = await file_discovery.get_files()
        discovered_file_paths = {str(f.resolve()) for f in discovered_files}

        path_str = str(path)

        # Check if path contains wildcard patterns
        if "*" in path_str or "?" in path_str or "[" in path_str:
            # Handle glob patterns
            matching_paths = glob.glob(path_str, recursive=True)
            if not matching_paths:
                return False

            success_count = 0
            for match_path in matching_paths:
                path_obj = Path(match_path).resolve()

                # Only add files that are in the discovery service and are actual files
                if path_obj.is_file() and str(path_obj) in discovered_file_paths:
                    key = str(path_obj)
                    console.print(f"Added {key} as {mode.value}")
                    self._context_files[key] = FileContext(path=path_obj, mode=mode)
                    success_count += 1

            return success_count > 0
        else:
            # Handle single file path
            path_obj = Path(path).resolve()

            # Only add if file is in the discovery service
            if not path_obj.is_file() or str(path_obj) not in discovered_file_paths:
                return False

            key = str(path_obj)
            self._context_files[key] = FileContext(path=path_obj, mode=mode)

            await self._notify_file_added(key, mode)

            console.print(f"Added {key} as {mode.value}")

            # Emit event for UI updates and other interested components
            return True

    async def _notify_file_added(self, file_path: str, mode: FileMode):
        """Notify system that a file was added to context"""
        message_bus = await self.make(MessageBus)

        # Send the file added event
        await message_bus.broadcast(
            Message(
                type=MessageType.FILE_ADDED,
                payload={
                    "file_path": file_path,
                    "mode": mode.value,
                    "action": "context_added",
                },
            )
        )

    async def remove_file(self, path: Union[str, PathLike]) -> bool:
        """Remove a file from active context to reduce noise.

        Supports wildcard patterns like 'byte/*' to remove multiple files at once.
        Only removes files that are available in the FileDiscoveryService to ensure
        consistency with project file management.
        Usage: `await service.remove_file("old_file.py")`
        Usage: `await service.remove_file("src/*.py")` -> removes all Python files
        """
        file_discovery = await self.make(FileDiscoveryService)
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
                    relative_path = str(Path(context_path).relative_to(Path.cwd()))
                    if glob.fnmatch.fnmatch(
                        relative_path, path_str
                    ) or glob.fnmatch.fnmatch(context_path, path_str):
                        matching_paths.append(context_path)
                except ValueError:
                    # If can't make relative, try matching absolute path
                    if glob.fnmatch.fnmatch(context_path, path_str):
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
            path_obj = Path(path).resolve()
            key = str(path_obj)

            # Only remove if file is in context and in discovery service
            if key in self._context_files and key in discovered_file_paths:
                del self._context_files[key]
                # await self.event(FileRemoved(file_path=str(path_obj)))
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
            # old_mode = self._context_files[key].mode
            self._context_files[key].mode = mode
            # await self.event(
            #     FileModeChanged(
            #         file_path=str(path_obj), old_mode=old_mode, new_mode=mode
            #     )
            # )
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
        # await self.event(ContextCleared())

    # Project file discovery methods
    async def get_project_files(self, extension: Optional[str] = None) -> List[str]:
        """Get all project files as relative path strings.

        Uses the discovery service to provide fast access to all project files,
        optionally filtered by extension for language-specific operations.
        Usage: `py_files = service.get_project_files('.py')` -> Python files
        """
        file_discovery = await self.make(FileDiscoveryService)
        return await file_discovery.get_relative_paths(extension)

    async def find_project_files(self, pattern: str) -> List[str]:
        """Find project files matching a pattern for completions.

        Provides fast file path completion by searching the cached project
        file index, respecting gitignore patterns automatically.
        Usage: `matches = service.find_project_files('src/main')` -> matching files
        """
        file_discovery = await self.make(FileDiscoveryService)
        matches = await file_discovery.find_files(pattern)

        if not self._config.project_root:
            return [str(f) for f in matches]
        return [str(f.relative_to(self._config.project_root)) for f in matches]

    async def is_file_in_context(self, path: Union[str, PathLike]) -> bool:
        """Check if a file is currently in the AI context.

        Quick lookup to determine if a file is already being tracked,
        useful for command validation and UI state management.
        Usage: `in_context = service.is_file_in_context("main.py")`
        """
        path_obj = Path(path).resolve()
        return str(path_obj) in self._context_files

    async def list_in_context_files(self):
        """Display current editable files before each prompt.

        Provides visual feedback about which files the AI can modify,
        helping users understand the current context state.
        """

        console = await self.make(Console)

        file_service = await self.make(FileService)
        editable_files = file_service.list_files(FileMode.EDITABLE)
        if editable_files:
            file_names = [f"[text]{f.relative_path}[/text]" for f in editable_files]
            console.print(
                Panel(
                    Columns(file_names, equal=True, expand=True),
                    title=f"[bold success]Editable Files ({len(editable_files)})[/bold success]",
                    border_style="success",
                )
            )

        readonly_files = file_service.list_files(FileMode.READ_ONLY)
        if readonly_files:
            file_names = [f"[text]{f.relative_path}[/text]" for f in readonly_files]
            console.print(
                Panel(
                    Columns(file_names, equal=True, expand=True),
                    title=f"[bold info]Read-only Files ({len(readonly_files)})[/bold info]",
                    border_style="info",
                )
            )

        return
