import glob
from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from rich.columns import Columns

from byte.core.event_bus import EventType, Payload
from byte.core.service.base_service import Service
from byte.core.utils import list_to_multiline_text
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.models import FileContext, FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary


class FileService(Service):
    """Simplified domain service for file context management with project discovery.

    Manages the active set of files available to the AI assistant, with
    integrated project file discovery for better completions and file operations.
    Loads all project files on boot for fast reference and completion.
    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """

    async def boot(self, **kwargs) -> None:
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

            # If the file is already in context, return False
            if key in self._context_files:
                return False

            self._context_files[key] = FileContext(path=path_obj, mode=mode)

            await self._notify_file_added(key, mode)

            # Emit event for UI updates and other interested components
            return True

    async def _notify_file_added(self, file_path: str, mode: FileMode):
        """Notify system that a file was added to context"""

        payload = Payload(
            event_type=EventType.FILE_ADDED,
            data={
                "file_path": file_path,
                "mode": mode.value,
                "action": "context_added",
            },
        )

        await self.emit(payload)

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
                    if glob.fnmatch.fnmatch(relative_path, path_str) or glob.fnmatch.fnmatch(context_path, path_str):
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
            # Create a new FileContext with the updated mode
            old_context = self._context_files[key]
            self._context_files[key] = FileContext(path=old_context.path, mode=mode)
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

    async def generate_context_prompt(self) -> tuple[list[str], list[str]]:
        """Generate structured file lists for read-only and editable files.

        Returns two separate lists of formatted file strings, enabling
        flexible assembly in the prompt context. The AI can understand
        its permissions and make appropriate suggestions for each file type.

        Returns:
                Tuple of (read_only_files, editable_files) as lists of strings

        Usage: `read_only, editable = await service.generate_context_prompt()`
        """
        read_only_files = []
        editable_files = []

        if not self._context_files:
            return (read_only_files, editable_files)

        # Separate files by mode for clear AI understanding
        read_only = [f for f in self._context_files.values() if f.mode == FileMode.READ_ONLY]
        editable = [f for f in self._context_files.values() if f.mode == FileMode.EDITABLE]

        if read_only:
            for file_ctx in sorted(read_only, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    content = await self._emit_file_context_event(file_ctx.relative_path, FileMode.READ_ONLY, content)
                    language = file_ctx.language
                    opening = Boundary.open(
                        BoundaryType.FILE,
                        meta={"source": file_ctx.relative_path, "language": language, "mode": "read-only"},
                    )
                    read_only_files.append(
                        list_to_multiline_text(
                            [
                                f"{opening}",
                                f"```{language}",
                                f"{content}",
                                "```",
                                Boundary.close(BoundaryType.FILE),
                            ]
                        )
                    )

        if editable:
            for file_ctx in sorted(editable, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    content = await self._emit_file_context_event(file_ctx.relative_path, FileMode.EDITABLE, content)
                    language = file_ctx.language
                    opening = Boundary.open(
                        BoundaryType.FILE,
                        meta={"source": file_ctx.relative_path, "language": language, "mode": "editable"},
                    )
                    editable_files.append(
                        list_to_multiline_text(
                            [
                                f"{opening}",
                                f"```{language}",
                                f"{content}",
                                "```",
                                Boundary.close(BoundaryType.FILE),
                            ]
                        )
                    )

        return (read_only_files, editable_files)

    async def generate_project_hierarchy(self, max_depth: int = 8, max_files_per_dir: int = 5) -> str:
        """Generate a concise project hierarchy for LLM understanding.

        Creates a tree-like structure showing directories and a sample of files,
        with special attention to root-level configuration files. Shows a limited
        number of files per directory with a count of additional files.

        Args:
                max_depth: Maximum directory depth to traverse (default: 8)
                max_files_per_dir: Maximum number of files to show per directory (default: 5)

        Returns:
                Formatted string representing the project structure

        Usage: `hierarchy = await service.generate_project_hierarchy()` -> tree structure
        """
        if not self._config.project_root:
            return "No project root configured"

        file_discovery = await self.make(FileDiscoveryService)
        all_files = await file_discovery.get_files()

        # Build directory structure
        dir_structure: Dict[Path, List[Path]] = {}
        root_files: List[Path] = []

        for file_path in all_files:
            try:
                relative = file_path.relative_to(self._config.project_root)
                parts = relative.parts

                # Check if it's a root file - include all root files
                if len(parts) == 1:
                    root_files.append(relative)
                else:
                    # Track all files regardless of depth
                    parent = Path(*parts[:-1])
                    if parent not in dir_structure:
                        dir_structure[parent] = []
                    dir_structure[parent].append(relative)
            except ValueError:
                continue

        # Build the hierarchy string
        lines = ["Project Structure:", ""]

        # Add root files first
        if root_files:
            for file in sorted(root_files):
                lines.append(f"├── {file}")
            lines.append("")

        # Add directories with limited file samples
        dirs_by_depth: Dict[int, List[Path]] = {}
        for dir_path in dir_structure.keys():
            depth = len(dir_path.parts)
            if depth not in dirs_by_depth:
                dirs_by_depth[depth] = []
            dirs_by_depth[depth].append(dir_path)

        # Sort and display directories by depth
        for depth in sorted(dirs_by_depth.keys()):
            if depth > max_depth:
                continue

            for dir_path in sorted(dirs_by_depth[depth]):
                indent = "│   " * (depth - 1) + "├── "
                files = sorted(dir_structure[dir_path])
                total_files = len(files)

                # Show directory with total file count
                lines.append(f"{indent}{dir_path.parts[-1]}/ ({total_files} files)")

                # Show sample of files
                files_to_show = files[:max_files_per_dir]
                file_indent = "│   " * depth + "├── "

                for file in files_to_show:
                    lines.append(f"{file_indent}{file.name}")

                # Add "X more files" message if there are more
                remaining = total_files - len(files_to_show)
                if remaining > 0:
                    lines.append(f"{file_indent}... {remaining} more files")

        return "\n".join(lines)

    async def _emit_file_context_event(self, file: str, type, content: str) -> str:
        """ """
        payload = Payload(
            event_type=EventType.GENERATE_FILE_CONTEXT,
            data={
                "file": file,
                "type": type,
                "content": content,
            },
        )

        payload = await self.emit(payload)
        return payload.get("content", content)

    async def clear_context(self):
        """Clear all files from context for fresh start.

        Useful when switching tasks or when context becomes too large
        for effective AI processing, enabling a clean slate approach.
        Usage: `await service.clear_context()` -> empty context
        """
        self._context_files.clear()

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

    async def list_in_context_files_hook(self, payload: Payload):
        """Display current editable files before each prompt.

        Provides visual feedback about which files the AI can modify,
        helping users understand the current context state.
        """

        console = await self.make(ConsoleService)

        info_panel = payload.get("info_panel", [])

        read_only_panel = None

        file_service = await self.make(FileService)
        readonly_files = file_service.list_files(FileMode.READ_ONLY)
        if readonly_files:
            file_names = [f"[text]{f.relative_path}[/text]" for f in readonly_files]
            read_only_panel = console.panel(
                Columns(file_names, equal=True, expand=True),
                title=f"Read-only Files ({len(readonly_files)})",
            )

        editable_panel = None
        editable_files = file_service.list_files(FileMode.EDITABLE)
        if editable_files:
            file_names = [f"[text]{f.relative_path}[/text]" for f in editable_files]
            editable_panel = console.panel(
                Columns(file_names, equal=True, expand=True),
                title=f"Editable Files ({len(editable_files)})",
            )

        # Create columns layout with both panels if they exist
        panels_to_show = []
        if read_only_panel:
            panels_to_show.append(read_only_panel)
        if editable_panel:
            panels_to_show.append(editable_panel)

        if panels_to_show:
            columns_panel = Columns(panels_to_show, equal=True, expand=True)
            info_panel.append(columns_panel)

        return payload.set("info_panel", info_panel)

    async def generate_context_prompt_with_line_numbers(self) -> tuple[list[str], list[str]]:
        """Generate structured file lists with line numbers for read-only and editable files.

        Similar to generate_context_prompt but includes line numbers for each line,
        making it easier for the research agent to identify specific lines when
        using LSP tools that require line numbers.

        Returns:
                Tuple of (read_only_files, editable_files) as lists of strings with line numbers

        Usage: `read_only, editable = await service.generate_context_prompt_with_line_numbers()`
        """
        read_only_files = []
        editable_files = []

        if not self._context_files:
            return (read_only_files, editable_files)

        # Separate files by mode for clear AI understanding
        read_only = [f for f in self._context_files.values() if f.mode == FileMode.READ_ONLY]
        editable = [f for f in self._context_files.values() if f.mode == FileMode.EDITABLE]

        if read_only:
            for file_ctx in sorted(read_only, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    content = await self._emit_file_context_event(file_ctx.relative_path, FileMode.READ_ONLY, content)
                    # Add line numbers to content
                    lines = content.splitlines()
                    numbered_lines = [f"{i:4d} | {line}" for i, line in enumerate(lines)]
                    numbered_content = "\n".join(numbered_lines)
                    language = file_ctx.language
                    opening = Boundary.open(
                        BoundaryType.FILE,
                        meta={"source": file_ctx.relative_path, "language": language, "mode": "read-only"},
                    )
                    closing = Boundary.close(BoundaryType.FILE)
                    read_only_files.append(f"{opening}\n{numbered_content}\n{closing}")

        if editable:
            for file_ctx in sorted(editable, key=lambda f: f.relative_path):
                content = file_ctx.get_content()
                if content is not None:
                    content = await self._emit_file_context_event(file_ctx.relative_path, FileMode.EDITABLE, content)
                    # Add line numbers to content
                    lines = content.splitlines()
                    numbered_lines = [f"{i + 1:4d} | {line}" for i, line in enumerate(lines)]
                    numbered_content = "\n".join(numbered_lines)
                    language = file_ctx.language
                    opening = Boundary.open(
                        BoundaryType.FILE,
                        meta={"source": file_ctx.relative_path, "language": language, "mode": "editable"},
                    )
                    closing = Boundary.close(BoundaryType.FILE)
                    editable_files.append(f"{opening}\n{numbered_content}\n{closing}")

        return (read_only_files, editable_files)
