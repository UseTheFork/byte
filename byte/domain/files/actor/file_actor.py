from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.core.logging import log
from byte.domain.files.service.file_service import FileService
from byte.domain.files.service.watcher_service import FileWatcherService


class FileActor(Actor):
    """Actor for handling file-related operations and events.

    Coordinates file context management, watches for file changes,
    and handles file-related commands through the actor system.
    Integrates with FileService and FileWatcherService for domain logic.
    """

    async def boot(self):
        await super().boot()
        self.file_service = None
        self.watcher_service = None

    async def on_start(self):
        """Initialize file services when actor starts"""
        log.info("file actor start")
        self.file_service = await self.make(FileService)
        self.watcher_service = await self.make(FileWatcherService)

    async def handle_message(self, message: Message):
        if message.type == MessageType.SHUTDOWN:
            await self._handle_shutdown()
        elif message.type == MessageType.FILE_CHANGE:
            await self._handle_file_change(message.payload)
        elif message.type == MessageType.FILE_ADDED:
            await self._handle_file_added(message.payload)
        elif message.type == MessageType.FILE_REMOVED:
            await self._handle_file_removed(message.payload)
        # Add other file-related message types as needed

    async def _handle_shutdown(self):
        """Clean shutdown of file watching and services"""
        if self.watcher_service:
            await self.watcher_service.stop_watching()
        await self.stop()

    async def _handle_file_change(self, payload):
        """Handle file system change notifications"""
        file_path = payload.get("file_path")
        change_type = payload.get("change_type")

        # Delegate to appropriate service methods
        if change_type == "modified" and self.file_service:
            # Check if file is in context and needs updates
            if await self.file_service.is_file_in_context(file_path):
                # Could emit events for UI updates or other actors
                pass

    async def _handle_file_added(self, payload):
        """Handle file addition events"""
        # file_path = payload.get("file_path")
        # Handle new file detection, possibly auto-add to context
        pass

    async def _handle_file_removed(self, payload):
        """Handle file removal events"""
        file_path = payload.get("file_path")
        if self.file_service:
            # Remove from context if it was being tracked
            await self.file_service.remove_file(file_path)

    async def subscriptions(self):
        """Subscribe to file-related message types"""
        return [
            MessageType.SHUTDOWN,
            MessageType.FILE_CHANGE,
            MessageType.FILE_ADDED,
            MessageType.FILE_REMOVED,
        ]
