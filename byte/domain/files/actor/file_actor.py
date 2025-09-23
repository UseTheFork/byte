import asyncio
import time
import uuid

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.file_service import FileService
from byte.domain.files.service.watcher_service import FileWatcherService
from byte.domain.system.actor.coordinator_actor import CoordinatorActor


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

        self._operation_batch = []
        self._batch_timer = None
        self._batch_timeout = 0.1

    async def on_start(self):
        """Initialize file services when actor starts"""
        self.file_service = await self.make(FileService)
        self.watcher_service = await self.make(FileWatcherService)

    async def handle_message(self, message: Message):
        if message.type == MessageType.FILE_OPERATION_REQUEST:
            await self._handle_file_operation_request(message)
        elif message.type == MessageType.SHUTDOWN:
            await self._handle_shutdown()

    async def _handle_shutdown(self):
        """Clean shutdown of file watching and services"""
        if self.watcher_service:
            await self.watcher_service.stop_watching()
        await self.stop()

    async def _handle_file_operation_request(self, message: Message):
        """Handle file operation requests from any source"""
        operation = message.payload.get("operation")
        path = message.payload.get("path")
        mode_value = message.payload.get("mode")
        source = message.payload.get("source", "command")  # Track source
        reason = message.payload.get("reason", "user_request")

        # Convert mode string back to enum if needed
        if isinstance(mode_value, str):
            mode = FileMode(mode_value)
        else:
            mode = mode_value

        file_service = await self.make(FileService)

        # Check if already in context (for file watcher)
        if await file_service.is_file_in_context(path):
            return  # Already in context, no need to add

        # Perform the operation
        if operation == "add":
            success = await file_service.add_file(path, mode)
        elif operation == "remove":
            success = await file_service.remove_file(path)
        else:
            success = False

        if success:
            await self._add_to_batch(
                {
                    "operation": operation,
                    "file_path": str(path),
                    "mode": mode.value,
                    "source": source,
                    "reason": reason,
                    "timestamp": time.time(),
                    "success": True,
                }
            )

        if message.reply_to:
            await message.reply_to.put(
                Message(
                    type=MessageType.FILE_OPERATION_RESPONSE,
                    payload={
                        "success": success,
                        "operation": operation,
                        "file_path": str(path),
                        "reason": "already_in_context"
                        if not success and await file_service.is_file_in_context(path)
                        else None,
                    },
                )
            )

    async def _add_to_batch(self, operation: dict):
        """Batch file operations to prevent state thrashing"""
        self._operation_batch.append(operation)

        if self._batch_timer:
            self._batch_timer.cancel()

        self._batch_timer = asyncio.create_task(self._emit_batch())

    async def _emit_batch(self):
        """Emit batched operations to coordinator"""
        await asyncio.sleep(self._batch_timeout)

        if self._operation_batch:
            batch = self._operation_batch.copy()
            self._operation_batch.clear()

            # Send to CoordinatorActor for state management
            await self.send_to(
                CoordinatorActor,
                Message(
                    type=MessageType.FILE_OPERATIONS_BATCH,
                    payload={"operations": batch, "batch_id": str(uuid.uuid4())},
                ),
            )

    async def subscriptions(self):
        """Subscribe to file-related message types"""
        return [
            MessageType.SHUTDOWN,
            MessageType.FILE_CHANGE,
            MessageType.FILE_ADDED,
            MessageType.FILE_REMOVED,
        ]
