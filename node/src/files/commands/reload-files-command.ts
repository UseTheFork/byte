import { Command } from '../../cli/service/command-registry.ts'
import { FileDiscoveryService } from '../service/file-discovery-service.ts'

export class ReloadFilesCommand extends Command {
  get name(): string { return 'reload' }
  get description(): string { return 'Reload the file discovery cache' }

  async execute(_args: string): Promise<void> {
    const fileDiscovery = this.app.make<FileDiscoveryService>(FileDiscoveryService as never)
    const console = this.app.make<{ print(t: string): void }>('console')
    fileDiscovery.refresh()
    const count = fileDiscovery.getFiles().length
    console.print(`File cache reloaded: ${count} files discovered.`)
  }
}
