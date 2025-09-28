import re
from pathlib import Path
from typing import Set

from watchfiles import Change, awatch

from byte.core.service.base_service import Service
from byte.core.task_manager import TaskManager
from byte.domain.cli_input.service.prompt_toolkit_service import PromptToolkitService
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService


class FileWatcherService(Service):
    """Simple file watcher service using TaskManager for background monitoring.

    Watches project files for changes and AI comment patterns.
    Usage: Automatically started during boot to monitor file changes
    """

    async def boot(self) -> None:
        """Initialize file watcher with TaskManager integration."""
        self._watched_files: Set[Path] = set()
        self.task_manager = await self.make(TaskManager)

        self._ai_patterns = [
            re.compile(r"//.*?AI([:|@|!|\?])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            re.compile(r"#.*?AI([:|@|!|\?])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            re.compile(
                r"<!--.*?AI([:|@|!|\?])\s*(.*?)\s*-->",
                re.MULTILINE | re.DOTALL | re.IGNORECASE,
            ),
        ]

        await self._start_watching()

    async def _start_watching(self) -> None:
        """Start file system monitoring using TaskManager."""
        if not self._config.project_root or not self._config.project_root.exists():
            return

        # Get files to watch
        file_discovery = await self.make(FileDiscoveryService)
        discovered_files = await file_discovery.get_files()
        self._watched_files = set(discovered_files)

        # Start watching with TaskManager
        self.task_manager.start_task("file_watcher", self._watch_files())

    async def _watch_files(self) -> None:
        """Main file watching loop."""
        try:
            async for changes in awatch(str(self._config.project_root)):
                for change_type, file_path_str in changes:
                    file_path = Path(file_path_str)
                    await self._handle_file_change(file_path, change_type)
        except Exception as e:
            print(f"File watcher error: {e}")

    async def _handle_file_change(self, file_path: Path, change_type: Change) -> None:
        """Handle file system changes."""

        result = False
        if change_type == Change.deleted:
            self._watched_files.discard(file_path)
            file_service = await self.make(FileService)
            if await file_service.is_file_in_context(file_path):
                result = await file_service.remove_file(file_path)
        elif change_type in [Change.added, Change.modified]:
            result = await self._handle_file_modified(file_path)

        if result:
            prompt_toolkit_service = await self.make(PromptToolkitService)
            await prompt_toolkit_service.interrupt()

    async def _handle_file_modified(self, file_path: Path) -> bool:
        """Handle file modification by scanning for AI comments."""
        try:
            content = file_path.read_text(encoding="utf-8")
            return await self._scan_for_ai_comments(file_path, content)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            # TODO: Should prob make this a litle smarter
            return False

    async def _scan_for_ai_comments(self, file_path: Path, content: str) -> bool:
        """Scan file content for AI comment patterns."""
        result = False
        for pattern in self._ai_patterns:
            for match in pattern.finditer(content):
                ai_type = match.group(1).strip() if match.groups() else ":"

                if ai_type == ":":
                    result = await self._auto_add_file_to_context(
                        file_path, FileMode.EDITABLE
                    )
                elif ai_type == "@":
                    result = await self._auto_add_file_to_context(
                        file_path, FileMode.READ_ONLY
                    )

        return result

    async def _auto_add_file_to_context(
        self, file_path: Path, mode: FileMode = FileMode.EDITABLE
    ) -> bool:
        """Automatically add file to context when AI comment is detected."""
        file_service = await self.make(FileService)
        return await file_service.add_file(file_path, mode)

    def get_watched_files(self) -> Set[Path]:
        """Get the current set of files being watched."""
        return self._watched_files.copy()
