import { readdirSync } from 'fs'
import { join, relative, basename } from 'path'
import { Service } from '../../support/service.ts'
import { FileIgnoreService } from './file-ignore-service.ts'

export class FileDiscoveryService extends Service {
  static token = Symbol('FileDiscoveryService')
  private _allFiles: Set<string> = new Set()
  private _ignoreService!: FileIgnoreService
  private _rootPath!: string

  override boot(): void {
    this._rootPath = this.app.make<string>('path.root')
    this._ignoreService = this.app.make<FileIgnoreService>(FileIgnoreService as never)
    this._scanProjectFiles()
  }

  private _scanProjectFiles(): void {
    this._allFiles.clear()
    this._walk(this._rootPath)
  }

  private _walk(dir: string): void {
    let entries
    try {
      entries = readdirSync(dir, { withFileTypes: true })
    } catch {
      return
    }
    for (const entry of entries) {
      const fullPath = join(dir, entry.name)
      if (this._ignoreService.isIgnored(fullPath)) continue
      if (entry.isDirectory()) {
        this._walk(fullPath)
      } else if (entry.isFile()) {
        this._allFiles.add(fullPath)
      }
    }
  }

  getFiles(extension?: string): string[] {
    const files = [...this._allFiles]
    if (!extension) return files
    const ext = extension.startsWith('.') ? extension.slice(1) : extension
    return files.filter(f => f.endsWith(`.${ext}`))
  }

  getRelativePaths(extension?: string): string[] {
    return this.getFiles(extension).map(f => relative(this._rootPath, f))
  }

  findFiles(pattern: string): string[] {
    const tier1: string[] = []
    const tier2: string[] = []
    const tier3: string[] = []

    for (const f of this._allFiles) {
      const rel = relative(this._rootPath, f)
      const fname = basename(f)
      if (rel.startsWith(pattern)) tier1.push(f)
      else if (fname.includes(pattern)) tier2.push(f)
      else if (rel.includes(pattern)) tier3.push(f)
    }

    const sortByRel = (a: string, b: string) =>
      relative(this._rootPath, a).localeCompare(relative(this._rootPath, b))

    return [
      ...tier1.sort(sortByRel),
      ...tier2.sort(sortByRel),
      ...tier3.sort(sortByRel),
    ]
  }

  addFile(filePath: string): boolean {
    if (this._allFiles.has(filePath)) return false
    this._allFiles.add(filePath)
    return true
  }

  removeFile(filePath: string): boolean {
    return this._allFiles.delete(filePath)
  }

  refresh(): void {
    this._ignoreService.refresh()
    this._scanProjectFiles()
  }
}
