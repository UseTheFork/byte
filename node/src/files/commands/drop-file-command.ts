import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'

export class DropFileCommand extends Command {
  get name(): string { return 'drop' }
  get description(): string { return 'Remove a file from context' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
    if (!path) {
      console.printError('Usage: /drop <path>')
      return
    }
    const fileService = this.app.make<FileService>(FileService as never)
    const removed = await fileService.removeFile(path)
    if (removed) console.print(`Dropped: ${path}`)
    else console.printError(`File not in context: ${path}`)
  }

  override async getCompletions(text: string): Promise<string[]> {
    const fileService = this.app.make<FileService>(FileService as never)
    return fileService.listFiles()
      .filter(f => f.relativePath.includes(text))
      .map(f => f.relativePath)
  }
}
