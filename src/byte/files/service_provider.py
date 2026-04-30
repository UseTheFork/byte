from typing import List, Type

from byte import Command, EventBus, Service, ServiceProvider
from byte.files import (
    AddFileCommand,
    AICommentWatcherService,
    DeleteFileTool,
    DropFileCommand,
    EditFileTool,
    FileDiscoveryService,
    FileEvents,
    FileIgnoreService,
    FileService,
    FileWatcherService,
    ListFilesCommand,
    ListFilesTool,
    ReadFilesTool,
    ReadOnlyCommand,
    ReloadFilesCommand,
    ReplaceFileTool,
    SwitchModeCommand,
    ToolFileService,
    WriteFileTool,
)
from byte.orchestration import OrchestrationEvents
from byte.system import SystemEvents
from byte.tools import BaseTool


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    def services(self) -> List[Type[Service]]:
        return [
            FileIgnoreService,
            FileDiscoveryService,
            FileService,
            FileWatcherService,
            AICommentWatcherService,
            ToolFileService,
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

    def tools(self) -> List[Type[BaseTool]]:
        """"""
        return [
            EditFileTool,
            WriteFileTool,
            DeleteFileTool,
            ReplaceFileTool,
            ReadFilesTool,
            ListFilesTool,
        ]

    async def boot(self):
        """Boot file services and register commands with registry."""

        # Boots the filewatcher service in to the task manager
        file_watcher_service = self.app.make(FileWatcherService)
        self.app.booted(file_watcher_service._start_watching)

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = self.app.make(EventBus)
        # file_service = self.app.make(FileService)

        # Boot AI comment watcher if enabled
        config = self.app["config"]
        if config.files.watch.enable:
            ai_comment_watcher = self.app.make(AICommentWatcherService)

            # Register AI comment watcher event hooks
            # event_bus.on(
            #     EventType.POST_PROMPT_TOOLKIT.value,
            #     ai_comment_watcher.modify_user_request_hook,
            # )

            # TODO: Is this still needed?
            event_bus.on(
                OrchestrationEvents.GatherReinforcement,
                ai_comment_watcher.add_reinforcement_hook,
            )

            # Subscribe to file change events
            event_bus.on(
                FileEvents.FileChanged,
                ai_comment_watcher.handle_file_change,
            )

        event_bus.on(
            SystemEvents.PostBoot,
            self.boot_messages,
        )

    async def boot_messages(self, event: SystemEvents.PostBoot) -> SystemEvents.PostBoot:
        file_discovery = self.app.make(FileDiscoveryService)

        found_files = await file_discovery.get_files()
        event.messages.append(f"[$text-muted]Files Discovered:[/$text-muted] [$primary]{len(found_files)}[/$primary]")

        return event
