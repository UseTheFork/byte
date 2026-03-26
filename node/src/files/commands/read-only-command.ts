import { relative } from 'path'
import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'
import { FileMode } from '../models.ts'

export class ReadOnlyCommand extends Command {
  get name(): string { return 'read-only' }
  get description(): string { return 'Add a file to context as read-only' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
    if (!path) {
      console.printError('Usage: /read-only <path>')
      return
    }
    const fileService = this.app.make<FileService>(FileService as never)
    const added = await fileService.addFile(path, FileMode.READ_ONLY)
    if (added) console.print(`Added (read-only): ${path}`)
    else console.printError(`Could not add: ${path}`)
  }

  override async getCompletions(text: string): Promise<string[]> {
    const fileService = this.app.make<FileService>(FileService as never)
    const rootPath = this.app.make<string>('path.root')
    const matches = await fileService.findProjectFiles(text)
    return matches.map(f => relative(rootPath, f))
  }
}
