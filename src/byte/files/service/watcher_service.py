from pathlib import Path

from watchfiles import Change, awatch

from byte import EventType, Payload, Service, TaskManager
from byte.files import FileDiscoveryService, FileIgnoreService, FileService


class FileWatcherService(Service):
    """Simple file watcher service for monitoring file system changes.

    Watches project files for changes and updates the discovery service cache.
    Always active to keep file discovery up-to-date.
    Usage: Automatically started during boot to monitor file changes
    """

    def _watch_filter(self, change: Change, path: str) -> bool:
        """Filter function for watchfiles to ignore files based on ignore patterns.

        NOTE: This is a synchronous filter function required by watchfiles library.
        We cache the ignore service's pathspec for efficient synchronous filtering.
        Usage: Used internally by awatch to determine which file changes to process.
        """
        if not self.app["path"]:
            return True

        try:
            spec = self.ignore_service.get_pathspec()

            if not spec:
                return True

            file_path = Path(path)
            relative_path = file_path.relative_to(self.app["path"])

            is_ignored = spec.match_file(str(relative_path)) or spec.match_file(str(relative_path) + "/")

            return not is_ignored
        except (ValueError, RuntimeError) as e:
            # If we can't determine if the file should be ignored, allow it through
            # The handler will do additional checks
            self.app["log"].debug(f"Error in watch filter for {path}: {e}")
            return True

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

    async def _watch_files(self) -> None:
        """Main file watching loop."""
        try:
            async for changes in awatch(str(self.app["path"]), watch_filter=self._watch_filter):
                for change_type, file_path_str in changes:
                    self.app["log"].debug(f"File changed: {change_type} -> {file_path_str}")
                    file_path = Path(file_path_str)
                    await self._handle_file_change(file_path, change_type)
        except Exception as e:
            # log.exception(e)
            print(f"File watcher error: {e}")

    def _start_watching(self) -> None:
        """Start file system monitoring using TaskManager."""
        self.task_manager.start_task("file_watcher", self._watch_files())

    def boot(self) -> None:
        """Initialize file watcher with TaskManager integration."""
        self.task_manager = self.app.make(TaskManager)
        self.ignore_service = self.app.make(FileIgnoreService)
        self.file_discovery = self.app.make(FileDiscoveryService)
        self.file_service = self.app.make(FileService)

        self._start_watching()
