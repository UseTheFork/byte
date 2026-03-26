import type { FSWatcher } from 'chokidar'
import { watch } from 'chokidar'
import { Service } from '../../support/service.ts'
import { Payload } from '../../support/concerns/eventable.ts'
import { EventType } from '../../foundation/event-bus.ts'
import { FileIgnoreService } from './file-ignore-service.ts'
import { FileDiscoveryService } from './file-discovery-service.ts'
import { FileService } from './file-service.ts'

export class FileWatcherService extends Service {
  static token = Symbol('FileWatcherService')
  private _watcher: FSWatcher | null = null

  override boot(): void {}

  async startWatching(): Promise<void> {
    const rootPath = this.app.make<string>('path.root')
    const ignoreService = this.app.make<FileIgnoreService>(FileIgnoreService as never)
    const fileDiscovery = this.app.make<FileDiscoveryService>(FileDiscoveryService as never)
    const fileService = this.app.make<FileService>(FileService as never)

    this._watcher = watch(rootPath, {
      ignored: (filePath: string) => ignoreService.isIgnored(filePath),
      persistent: true,
      ignoreInitial: true,
    })

    this._watcher.on('add', (filePath: string) => {
      fileDiscovery.addFile(filePath)
      void this.emit(new Payload(EventType.FILE_CHANGED, { file_path: filePath, change_type: 'add' }))
    })

    this._watcher.on('change', (filePath: string) => {
      void this.emit(new Payload(EventType.FILE_CHANGED, { file_path: filePath, change_type: 'change' }))
    })

    this._watcher.on('unlink', async (filePath: string) => {
      fileDiscovery.removeFile(filePath)
      if (fileService.isFileInContext(filePath)) {
        await fileService.removeFile(filePath)
      }
      void this.emit(new Payload(EventType.FILE_CHANGED, { file_path: filePath, change_type: 'unlink' }))
    })
  }

  async stopWatching(): Promise<void> {
    if (this._watcher) {
      await this._watcher.close()
      this._watcher = null
    }
  }
}
