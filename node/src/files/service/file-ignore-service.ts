import { readFileSync, existsSync } from 'fs'
import { relative, isAbsolute, join } from 'path'
import ignore, { type Ignore } from 'ignore'
import { Service } from '../../support/service.ts'
import type { ByteConfig } from '../../config/schemas.ts'

export class FileIgnoreService extends Service {
  static token = Symbol('FileIgnoreService')
  private _ig!: Ignore
  private _rootPath!: string

  override boot(): void {
    this._rootPath = this.app.make<string>('path.root')
    this._loadIgnorePatterns()
  }

  private _loadIgnorePatterns(): void {
    const ig = ignore()
    const gitignorePath = join(this._rootPath, '.gitignore')
    if (existsSync(gitignorePath)) {
      ig.add(readFileSync(gitignorePath, 'utf-8'))
    }
    const config = this.app.make<ByteConfig>('config')
    for (const pattern of config.files.ignore) {
      ig.add(pattern)
    }
    this._ig = ig
  }

  isIgnored(filePath: string): boolean {
    let rel: string
    if (isAbsolute(filePath)) {
      try {
        rel = relative(this._rootPath, filePath)
      } catch {
        return true
      }
      if (rel.startsWith('..')) return true
    } else {
      rel = filePath
    }
    if (!rel || rel === '.') return false
    return this._ig.ignores(rel)
  }

  refresh(): void {
    this._loadIgnorePatterns()
  }

  getIgnore(): Ignore {
    return this._ig
  }
}
