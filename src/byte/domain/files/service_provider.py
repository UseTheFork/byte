from typing import List, Type

from byte.container import Container
from byte.core import ByteConfig, EventBus, EventType, Payload, Service, ServiceProvider
from byte.domain.cli import Command
from byte.domain.files import (
    AddFileCommand,
    AICommentWatcherService,
    DropFileCommand,
    FileDiscoveryService,
    FileIgnoreService,
    FileService,
    FileWatcherService,
    ListFilesCommand,
    ReadOnlyCommand,
    ReloadFilesCommand,
    SwitchModeCommand,
)


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    def services(self) -> List[Type[Service]]:
        return [
            FileIgnoreService,
            FileDiscoveryService,
            FileService,
            FileWatcherService,
            AICommentWatcherService,
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            ListFilesCommand,
            AddFileCommand,
            ReadOnlyCommand,
            DropFileCommand,
            SwitchModeCommand,
            ReloadFilesCommand,
        ]

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Ensure ignore service is booted first for pattern loading
        await container.make(FileIgnoreService)

        # Then boot file discovery which depends on ignore service
        await container.make(FileDiscoveryService)

        # Boots the filewatcher service in to the task manager
        await container.make(FileWatcherService)

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = await container.make(EventBus)
        file_service = await container.make(FileService)

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            EventType.PRE_PROMPT_TOOLKIT.value,
            file_service.list_in_context_files_hook,
        )

        # Boot AI comment watcher if enabled
        config = await container.make(ByteConfig)
        if config.files.watch.enable:
            ai_comment_watcher = await container.make(AICommentWatcherService)

            # Register AI comment watcher event hooks
            event_bus.on(
                EventType.POST_PROMPT_TOOLKIT.value,
                ai_comment_watcher.modify_user_request_hook,
            )

            event_bus.on(
                EventType.GATHER_REINFORCEMENT.value,
                ai_comment_watcher.add_reinforcement_hook,
            )

            # Subscribe to file change events
            event_bus.on(
                EventType.FILE_CHANGED.value,
                ai_comment_watcher.handle_file_change,
            )

        event_bus.on(
            EventType.POST_BOOT.value,
            self.boot_messages,
        )

    async def boot_messages(self, payload: Payload) -> Payload:
        container: Container = payload.get("container", False)
        if container:
            file_discovery = await container.make(FileDiscoveryService)
            messages = payload.get("messages", [])
            found_files = await file_discovery.get_files()
            messages.append(f"[muted]Files Discovered:[/muted] [primary]{len(found_files)}[/primary]")

            payload.set("messages", messages)

        return payload
