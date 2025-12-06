from pathlib import Path

from watchfiles import Change, awatch

from byte.core.event_bus import EventType, Payload
from byte.core.logging import log
from byte.core.service.base_service import Service
from byte.core.task_manager import TaskManager
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService
from byte.domain.files.service.ignore_service import FileIgnoreService


class FileWatcherService(Service):
    """Simple file watcher service for monitoring file system changes.

    Watches project files for changes and updates the discovery service cache.
    Always active to keep file discovery up-to-date.
    Usage: Automatically started during boot to monitor file changes
    """

    async def boot(self) -> None:
        """Initialize file watcher with TaskManager integration."""
        self.task_manager = await self.make(TaskManager)
        self.ignore_service = await self.make(FileIgnoreService)
        self.file_discovery = await self.make(FileDiscoveryService)
        self.file_service = await self.make(FileService)

        await self._start_watching()

    def _watch_filter(self, change: Change, path: str) -> bool:
        """Filter function for watchfiles to ignore files based on ignore patterns.

        NOTE: This is a synchronous filter function required by watchfiles library.
        We cache the ignore service's pathspec for efficient synchronous filtering.
        Usage: Used internally by awatch to determine which file changes to process.
        """
        if not self._config.project_root:
            return True

        try:
            spec = self.ignore_service.get_pathspec()

            if not spec:
                return True

            file_path = Path(path)
            relative_path = file_path.relative_to(self._config.project_root)

            is_ignored = spec.match_file(str(relative_path)) or spec.match_file(str(relative_path) + "/")

            return not is_ignored
        except (ValueError, RuntimeError):
            return False

    async def _start_watching(self) -> None:
        """Start file system monitoring using TaskManager."""
        self.task_manager.start_task("file_watcher", self._watch_files())

    async def _watch_files(self) -> None:
        """Main file watching loop."""
        try:
            async for changes in awatch(str(self._config.project_root), watch_filter=self._watch_filter):
                for change_type, file_path_str in changes:
                    log.debug(f"File changed: {change_type} -> {file_path_str}")
                    file_path = Path(file_path_str)
                    await self._handle_file_change(file_path, change_type)
        except Exception as e:
            log.exception(e)
            print(f"File watcher error: {e}")

    async def _handle_file_change(self, file_path: Path, change_type: Change) -> None:
        """Handle file system changes and update discovery cache."""
        if file_path.is_dir():
            return

        if change_type == Change.deleted:
            await self.file_discovery.remove_file(file_path)

            if await self.file_service.is_file_in_context(file_path):
                await self.file_service.remove_file(file_path)

        elif change_type == Change.added:
            await self.file_discovery.add_file(file_path)

        await self.emit(
            Payload(
                event_type=EventType.FILE_CHANGED,
                data={
                    "file_path": str(file_path),
                    "change_type": change_type.name.lower(),
                },
            )
        )
