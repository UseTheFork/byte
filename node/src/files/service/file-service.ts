import { join, isAbsolute, relative } from 'path'
import { Service } from '../../support/service.ts'
import { Boundary, BoundaryType } from '../../support/boundary.ts'
import { Payload } from '../../support/concerns/eventable.ts'
import { EventType } from '../../foundation/event-bus.ts'
import { FileDiscoveryService } from './file-discovery-service.ts'
import { FileContext, FileMode } from '../models.ts'

export class FileService extends Service {
  static token = Symbol('FileService')
  private _contextFiles: Map<string, FileContext> = new Map()
  private _rootPath!: string

  override boot(): void {
    this._rootPath = this.app.make<string>('path.root')
  }

  private _discovery(): FileDiscoveryService {
    return this.app.make<FileDiscoveryService>(FileDiscoveryService as never)
  }

  private _resolve(path: string): string {
    return isAbsolute(path) ? path : join(this._rootPath, path)
  }

  async addFile(path: string, mode: FileMode): Promise<boolean> {
    const isGlob = /[*?\[]/.test(path)
    const discovery = this._discovery()

    if (isGlob) {
      const glob = new Bun.Glob(path)
      const discoveredSet = new Set(discovery.getFiles())
      let added = false
      for (const match of glob.scanSync({ cwd: this._rootPath })) {
        const abs = join(this._rootPath, match)
        if (!this._contextFiles.has(abs) && discoveredSet.has(abs)) {
          this._contextFiles.set(abs, new FileContext(abs, mode, this._rootPath))
          added = true
        }
      }
      return added
    }

    const abs = this._resolve(path)
    if (this._contextFiles.has(abs)) return false
    if (!discovery.getFiles().includes(abs)) return false
    this._contextFiles.set(abs, new FileContext(abs, mode, this._rootPath))
    await this.emit(new Payload(EventType.FILE_ADDED, { file_path: abs }))
    return true
  }

  async removeFile(path: string): Promise<boolean> {
    const isGlob = /[*?\[]/.test(path)

    if (isGlob) {
      const glob = new Bun.Glob(path)
      const matches = new Set(
        [...glob.scanSync({ cwd: this._rootPath })].map(f => join(this._rootPath, f))
      )
      let removed = false
      for (const key of this._contextFiles.keys()) {
        if (matches.has(key)) {
          this._contextFiles.delete(key)
          removed = true
        }
      }
      return removed
    }

    return this._contextFiles.delete(this._resolve(path))
  }

  listFiles(mode?: FileMode): FileContext[] {
    const files = [...this._contextFiles.values()]
    const filtered = mode ? files.filter(f => f.mode === mode) : files
    return filtered.sort((a, b) => a.relativePath.localeCompare(b.relativePath))
  }

  setFileMode(path: string, mode: FileMode): boolean {
    const abs = this._resolve(path)
    if (!this._contextFiles.has(abs)) return false
    this._contextFiles.set(abs, new FileContext(abs, mode, this._rootPath))
    return true
  }

  getFileContext(path: string): FileContext | null {
    return this._contextFiles.get(this._resolve(path)) ?? null
  }

  isFileInContext(path: string): boolean {
    return this._contextFiles.has(this._resolve(path))
  }

  async getProjectFiles(extension?: string): Promise<string[]> {
    return this._discovery().getFiles(extension)
  }

  async findProjectFiles(pattern: string): Promise<string[]> {
    return this._discovery().findFiles(pattern)
  }

  clearContext(): void {
    this._contextFiles.clear()
  }

  async generateContextPrompt(): Promise<[string[], string[]]> {
    const readOnly: string[] = []
    const editable: string[] = []
    for (const ctx of this.listFiles()) {
      const content = ctx.getContent()
      if (content === null) continue
      const entry = [
        Boundary.open(BoundaryType.FILE, { path: ctx.relativePath }),
        `\`\`\`${ctx.language}`,
        content,
        '```',
        Boundary.close(BoundaryType.FILE),
      ].join('\n')
      if (ctx.mode === FileMode.READ_ONLY) readOnly.push(entry)
      else editable.push(entry)
    }
    return [readOnly, editable]
  }

  async generateContextPromptWithLineNumbers(): Promise<[string[], string[]]> {
    const readOnly: string[] = []
    const editable: string[] = []
    for (const ctx of this.listFiles()) {
      const content = ctx.getContent()
      if (content === null) continue
      const numbered = content
        .split('\n')
        .map((line, i) => `   ${i + 1} | ${line}`)
        .join('\n')
      const entry = [
        Boundary.open(BoundaryType.FILE, { path: ctx.relativePath }),
        `\`\`\`${ctx.language}`,
        numbered,
        '```',
        Boundary.close(BoundaryType.FILE),
      ].join('\n')
      if (ctx.mode === FileMode.READ_ONLY) readOnly.push(entry)
      else editable.push(entry)
    }
    return [readOnly, editable]
  }

  async generateProjectHierarchy(): Promise<string> {
    const allFiles = this._discovery().getFiles()
    const maxFilesPerDir = 5

    type DirNode = { files: string[]; dirs: Map<string, DirNode> }
    const root: DirNode = { files: [], dirs: new Map() }

    for (const f of allFiles) {
      const rel = relative(this._rootPath, f)
      const parts = rel.split('/')
      let node = root
      for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i]
        if (!node.dirs.has(part)) node.dirs.set(part, { files: [], dirs: new Map() })
        node = node.dirs.get(part)!
      }
      node.files.push(parts[parts.length - 1])
    }

    const hasFiles = (n: DirNode): boolean =>
      n.files.length > 0 || [...n.dirs.values()].some(hasFiles)

    const render = (node: DirNode, indent: string, isRoot: boolean): string => {
      const lines: string[] = []
      const sorted = node.files.sort()
      const visible = isRoot ? sorted : sorted.slice(0, maxFilesPerDir)
      const remaining = sorted.length - visible.length
      for (const f of visible) lines.push(`${indent}${f}`)
      if (remaining > 0) lines.push(`${indent}... ${remaining} more files`)
      for (const [name, sub] of [...node.dirs.entries()].sort(([a], [b]) => a.localeCompare(b))) {
        if (!hasFiles(sub)) continue
        lines.push(`${indent}${name}/`)
        lines.push(render(sub, `${indent}  `, false))
      }
      return lines.join('\n')
    }

    return [
      Boundary.open(BoundaryType.PROJECT_HIERARCHY),
      render(root, '', true),
      Boundary.close(BoundaryType.PROJECT_HIERARCHY),
    ].join('\n')
  }

  async listInContextFilesHook(payload: Payload): Promise<Payload> {
    const existing = (payload.get('info_panel') as string | undefined) ?? ''
    const readOnly = this.listFiles(FileMode.READ_ONLY)
    const editable = this.listFiles(FileMode.EDITABLE)
    let panel = existing
    if (readOnly.length > 0) {
      panel += '\nRead-only files:\n' + readOnly.map(f => `  ${f.relativePath}`).join('\n')
    }
    if (editable.length > 0) {
      panel += '\nEditable files:\n' + editable.map(f => `  ${f.relativePath}`).join('\n')
    }
    return payload.set('info_panel', panel)
  }
}
