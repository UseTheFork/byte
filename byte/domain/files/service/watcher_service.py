import asyncio
import re
from pathlib import Path
from typing import Dict, Set

from watchfiles import Change, awatch

from byte.core.service.base_service import Service
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService


class FileWatcherService(Service):
    """Service for monitoring file system changes and AI comment detection.

    Watches project files for changes, deletions, and AI comment patterns
    to automatically manage context and trigger completions. Integrates with
    FileDiscoveryService to only watch relevant project files.
    Usage: Automatically started during boot to monitor file changes
    """

    async def boot(self) -> None:
        """Initialize file watcher with discovery service integration."""
        self._watched_files: Set[Path] = set()
        self._debounce_tasks: Dict[Path, asyncio.Task] = {}
        self._watch_task: asyncio.Task = None

        # Comment patterns for different file types
        self._ai_patterns = [
            # JavaScript, C++, etc.
            re.compile(r"//.*?AI([:|@|!|\?])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            # Python, shell, etc.
            re.compile(r"#.*?AI([:|@|!|\?])\s*(.*)$", re.MULTILINE | re.IGNORECASE),
            # HTML, XML
            re.compile(
                r"<!--.*?AI([:|@|!|\?])\s*(.*?)\s*-->",
                re.MULTILINE | re.DOTALL | re.IGNORECASE,
            ),
        ]

        await self._start_watching()

    async def _start_watching(self) -> None:
        """Start file system monitoring for the project directory."""
        if not self._config.project_root or not self._config.project_root.exists():
            return

        # Get initial set of files to watch from discovery service
        file_discovery = await self.make(FileDiscoveryService)
        discovered_files = await file_discovery.get_files()
        self._watched_files = set(discovered_files)

        # Start the watch task
        self._watch_task = asyncio.create_task(self._watch_files())

    async def _watch_files(self) -> None:
        """Main file watching loop using watchfiles."""
        try:
            async for changes in awatch(str(self._config.project_root)):
                for change_type, file_path_str in changes:
                    file_path = Path(file_path_str)

                    # Convert watchfiles.Change enum to string
                    if change_type == Change.added:
                        change_str = "created"
                    elif change_type == Change.modified:
                        change_str = "modified"
                    elif change_type == Change.deleted:
                        change_str = "deleted"
                    else:
                        continue  # Skip unknown change types

                    # Handle the file change
                    await self._handle_file_change(file_path, change_str)
        except asyncio.CancelledError:
            # Task was cancelled, clean shutdown
            pass
        except Exception as e:
            # Log error but don't crash the service
            print(f"File watcher error: {e}")

    async def _handle_file_change(self, file_path: Path, change_type: str) -> None:
        """Handle file system change with debouncing to prevent spam."""
        # Cancel existing debounce task for this file
        if file_path in self._debounce_tasks:
            self._debounce_tasks[file_path].cancel()

        # Create new debounced task
        self._debounce_tasks[file_path] = asyncio.create_task(
            self._debounced_file_change(file_path, change_type)
        )

    async def _debounced_file_change(self, file_path: Path, change_type: str) -> None:
        """Process file change after debounce delay."""
        try:
            # Wait for debounce period
            debounce_ms = 500  # Default fallback
            # if hasattr(self._config, "files") and hasattr(self._config.files, "watch"):
            #     debounce_ms = self._config.files.watch.debounce_ms

            await asyncio.sleep(debounce_ms / 1000.0)

            # Only process files we're supposed to be watching
            if change_type != "deleted" and file_path not in self._watched_files:
                # Check if this is a new file we should watch
                file_discovery = await self.make(FileDiscoveryService)
                await file_discovery.refresh()  # Refresh to pick up new files
                discovered_files = await file_discovery.get_files()

                if file_path in discovered_files:
                    self._watched_files.add(file_path)
                else:
                    return  # Not a file we should watch

            # Emit file change event
            # await self.event(
            #     FileModified(file_path=str(file_path), change_type=change_type)
            # )

            if change_type == "deleted":
                await self._handle_file_deleted(file_path)
            elif change_type in ["created", "modified"]:
                await self._handle_file_modified(file_path)

        except asyncio.CancelledError:
            # Task was cancelled due to new change, ignore
            pass
        finally:
            # Clean up debounce task
            self._debounce_tasks.pop(file_path, None)

    async def _handle_file_deleted(self, file_path: Path) -> None:
        """Handle file deletion by removing from context and updating watch list."""
        # Remove from watched files
        self._watched_files.discard(file_path)

        # Emit deletion event for other services to handle
        # await self.event(FileDeleted(file_path=str(file_path)))

        # Remove from file service context if present
        file_service = await self.make(FileService)
        if await file_service.is_file_in_context(file_path):
            await file_service.remove_file(file_path)

    async def _handle_file_modified(self, file_path: Path) -> None:
        """Handle file modification by scanning for AI comments."""
        # Check if AI comment patterns are enabled
        # if not (
        #     hasattr(self._config, "files")
        #     and hasattr(self._config.files, "watch")
        #     and self._config.files.watch.ai_comment_patterns
        # ):
        #     return

        try:
            content = file_path.read_text(encoding="utf-8")
            await self._scan_for_ai_comments(file_path, content)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            # File might be temporarily unavailable or binary
            pass

    async def _scan_for_ai_comments(self, file_path: Path, content: str) -> None:
        """Scan file content for AI comment patterns."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Collect all matches from all patterns on this line
            all_matches = []

            for pattern in self._ai_patterns:
                # Use finditer to get all matches, not just the first one
                for match in pattern.finditer(line):
                    ai_type = match.group(1).strip() if match.groups() else ":"
                    comment_content = (
                        match.group(2).strip() if len(match.groups()) > 1 else ""
                    )
                    all_matches.append((ai_type, comment_content, match.start()))

            # Sort matches by position in line to process them in order
            all_matches.sort(key=lambda x: x[2])

            # Process each match found on this line
            for ai_type, comment_content, _ in all_matches:
                # Emit AI comment detected event
                # await self.event(
                #     AICommentDetected(
                #         file_path=str(file_path),
                #         comment_content=comment_content,
                #         line_number=line_num,
                #     )
                # )

                # Handle different AI comment types
                if ai_type == ":":
                    # Add file to editable context
                    await self._auto_add_file_to_context(file_path, FileMode.EDITABLE)
                elif ai_type == "@":
                    # Add file to read-only context
                    await self._auto_add_file_to_context(file_path, FileMode.READ_ONLY)

                if ai_type == "!":
                    pass
                    # Trigger completion request for coder service
                    # await self.event(
                    #     CompletionRequested(
                    #         file_path=str(file_path),
                    #         task=comment_content,
                    #         line_number=line_num,
                    #     )
                    # )
                elif ai_type == "?":
                    pass
                    # Trigger ask request for question answering
                    # from byte.domain.files.events import AskRequested

                    # await self.event(
                    #     AskRequested(
                    #         file_path=str(file_path),
                    #         question=comment_content,
                    #         line_number=line_num,
                    #     )
                    # )

    async def _auto_add_file_to_context(
        self, file_path: Path, mode: FileMode = FileMode.EDITABLE
    ) -> None:
        """Automatically add file to context when AI comment is detected."""
        # Send request to FileActor instead of direct service call
        pass

    async def stop_watching(self) -> None:
        """Stop file system monitoring and cleanup resources."""
        if self._watch_task and not self._watch_task.done():
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass

        # Cancel any pending debounce tasks
        for task in self._debounce_tasks.values():
            task.cancel()
        self._debounce_tasks.clear()

    async def refresh_watched_files(self) -> None:
        """Refresh the list of files being watched from discovery service."""
        file_discovery = await self.make(FileDiscoveryService)
        await file_discovery.refresh()
        discovered_files = await file_discovery.get_files()
        self._watched_files = set(discovered_files)

    def get_watched_files(self) -> Set[Path]:
        """Get the current set of files being watched."""
        return self._watched_files.copy()
