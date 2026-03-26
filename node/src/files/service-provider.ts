import { ServiceProvider } from '../support/service-provider.ts'
import { CommandRegistry } from '../cli/service/command-registry.ts'
import { EventBus, EventType } from '../foundation/event-bus.ts'
import type { ByteConfig } from '../config/schemas.ts'
import { FileIgnoreService } from './service/file-ignore-service.ts'
import { FileDiscoveryService } from './service/file-discovery-service.ts'
import { FileService } from './service/file-service.ts'
import { FileWatcherService } from './service/file-watcher-service.ts'
import { AICommentWatcherService } from './service/ai-comment-watcher-service.ts'
import { AddFileCommand } from './commands/add-file-command.ts'
import { ReadOnlyCommand } from './commands/read-only-command.ts'
import { DropFileCommand } from './commands/drop-file-command.ts'
import { ListFilesCommand } from './commands/list-files-command.ts'
import { SwitchModeCommand } from './commands/switch-mode-command.ts'
import { ReloadFilesCommand } from './commands/reload-files-command.ts'

export class FilesServiceProvider extends ServiceProvider {
  override register(): void {
    this.app.singleton(FileIgnoreService as never, () => {
      const svc = new FileIgnoreService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(FileDiscoveryService as never, () => {
      const svc = new FileDiscoveryService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(FileService as never, () => {
      const svc = new FileService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(FileWatcherService as never, () => {
      const svc = new FileWatcherService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(AICommentWatcherService as never, () => {
      const svc = new AICommentWatcherService(this.app)
      svc.ensureBooted()
      return svc
    })
  }

  override async boot(): Promise<void> {
    const registry = this.app.make<CommandRegistry>('command-registry')
    registry.register(new AddFileCommand(this.app))
    registry.register(new ReadOnlyCommand(this.app))
    registry.register(new DropFileCommand(this.app))
    registry.register(new ListFilesCommand(this.app))
    registry.register(new SwitchModeCommand(this.app))
    registry.register(new ReloadFilesCommand(this.app))

    const eventBus = this.app.make<EventBus>('event-bus')
    const fileService = this.app.make<FileService>(FileService as never)
    const fileWatcher = this.app.make<FileWatcherService>(FileWatcherService as never)

    void fileWatcher.startWatching()

    eventBus.on(EventType.PRE_PROMPT_TOOLKIT, (payload) =>
      fileService.listInContextFilesHook(payload)
    )

    eventBus.on(EventType.POST_BOOT, async (payload) => {
      const discovery = this.app.make<FileDiscoveryService>(FileDiscoveryService as never)
      const console = this.app.make<{ print(t: string): void }>('console')
      console.print(`Discovered ${discovery.getFiles().length} files.`)
      return payload
    })

    const config = this.app.make<ByteConfig>('config')
    if (config.files.watch.enable) {
      const aiWatcher = this.app.make<AICommentWatcherService>(AICommentWatcherService as never)
      eventBus.on(EventType.POST_PROMPT_TOOLKIT, (payload) =>
        aiWatcher.modifyUserRequestHook(payload)
      )
      eventBus.on(EventType.GATHER_REINFORCEMENT, (payload) =>
        aiWatcher.addReinforcementHook(payload)
      )
      eventBus.on(EventType.FILE_CHANGED, (payload) =>
        aiWatcher.handleFileChange(payload)
      )
    }
  }

  override async shutdown(): Promise<void> {
    const fileWatcher = this.app.make<FileWatcherService>(FileWatcherService as never)
    await fileWatcher.stopWatching()
  }
}
