import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'
import { FileMode } from '../models.ts'

export class ListFilesCommand extends Command {
  get name(): string { return 'ls' }
  get description(): string { return 'List files in context' }

  async execute(_args: string): Promise<void> {
    const fileService = this.app.make<FileService>(FileService as never)
    const console = this.app.make<{ print(t: string): void }>('console')
    const readOnly = fileService.listFiles(FileMode.READ_ONLY)
    const editable = fileService.listFiles(FileMode.EDITABLE)

    if (readOnly.length === 0 && editable.length === 0) {
      console.print('No files in context.')
      return
    }
    if (readOnly.length > 0) {
      console.print('Read-only:')
      for (const f of readOnly) console.print(`  ${f.relativePath}`)
    }
    if (editable.length > 0) {
      console.print('Editable:')
      for (const f of editable) console.print(`  ${f.relativePath}`)
    }
  }
}
