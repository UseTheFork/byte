from byte import EventBus, ServiceProvider
from byte.files import (
    AddFileCommand,
    AddFilesTool,
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
    ReloadFilesCommand,
    ReplaceFileTool,
    ToolFileService,
    WriteFileTool,
)
from byte.orchestration import OrchestrationEvents
from byte.system import SystemEvents


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    def services(self):
        return [
            # keep-sorted start
            AICommentWatcherService,
            FileDiscoveryService,
            FileIgnoreService,
            FileService,
            FileWatcherService,
            ToolFileService,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            AddFileCommand,
            DropFileCommand,
            ListFilesCommand,
            ReloadFilesCommand,
            # keep-sorted end
        ]

    def tools(self):
        """"""
        return [
            # keep-sorted start
            AddFilesTool,
            DeleteFileTool,
            EditFileTool,
            ListFilesTool,
            ReplaceFileTool,
            WriteFileTool,
            # keep-sorted end
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
