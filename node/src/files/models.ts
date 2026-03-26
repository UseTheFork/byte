import { readFileSync } from 'fs'
import { relative } from 'path'
import { getLanguageFromFilename } from '../support/utils/get-language-from-filename.ts'

export enum FileMode {
  READ_ONLY = 'read_only',
  EDITABLE  = 'editable',
}

export class FileContext {
  constructor(
    public readonly path:     string,
    public readonly mode:     FileMode,
    public readonly rootPath: string,
  ) {}

  get language(): string {
    return getLanguageFromFilename(this.path) ?? 'text'
  }

  get relativePath(): string {
    try {
      return relative(this.rootPath, this.path)
    } catch {
      return this.path
    }
  }

  getContent(): string | null {
    try {
      return readFileSync(this.path, 'utf-8')
    } catch {
      return null
    }
  }
}
