import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'
import { FileMode } from '../models.ts'

export class SwitchModeCommand extends Command {
  get name(): string { return 'switch' }
  get description(): string { return 'Toggle a context file between read-only and editable' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    if (!path) {
      const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
      console.printError('Usage: /switch <path>')
      return
    }
    const fileService = this.app.make<FileService>(FileService as never)
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
    const ctx = fileService.getFileContext(path)
    if (!ctx) {
      console.printError(`File not in context: ${path}`)
      return
    }
    const newMode = ctx.mode === FileMode.READ_ONLY ? FileMode.EDITABLE : FileMode.READ_ONLY
    fileService.setFileMode(path, newMode)
    console.print(`${ctx.relativePath} → ${newMode}`)
  }

  override async getCompletions(text: string): Promise<string[]> {
    const fileService = this.app.make<FileService>(FileService as never)
    return fileService.listFiles()
      .filter(f => f.relativePath.includes(text))
      .map(f => f.relativePath)
  }
}
