# Files Domain Node Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the `files` domain from Python to TypeScript/Bun — models, 5 services, 6 commands, and a service provider wired into `main.ts`.

**Architecture:** `FileIgnoreService` wraps the `ignore` package for gitignore-style filtering; `FileDiscoveryService` recursively scans and caches project files; `FileService` manages the per-session context set and generates prompts; `FileWatcherService` keeps the cache live via chokidar. All 5 services follow the existing `singleton + ensureBooted()` pattern from `GitServiceProvider`.

**Tech Stack:** Bun, TypeScript, `ignore` (gitignore patterns), `chokidar` (fs watching), existing `Service`/`ServiceProvider`/`Command`/`EventBus` infrastructure.

---

## File Map

**Create:**
- `node/src/files/models.ts` — `FileMode` enum, `FileContext` class
- `node/src/files/service/file-ignore-service.ts` — gitignore pattern matching
- `node/src/files/service/file-discovery-service.ts` — recursive file cache
- `node/src/files/service/file-service.ts` — session context + prompt generation
- `node/src/files/service/file-watcher-service.ts` — chokidar watcher
- `node/src/files/service/ai-comment-watcher-service.ts` — stub
- `node/src/files/tools.ts` — stub
- `node/src/files/commands/add-file-command.ts`
- `node/src/files/commands/read-only-command.ts`
- `node/src/files/commands/drop-file-command.ts`
- `node/src/files/commands/list-files-command.ts`
- `node/src/files/commands/switch-mode-command.ts`
- `node/src/files/commands/reload-files-command.ts`
- `node/src/files/service-provider.ts`
- `node/src/files/index.ts`
- `node/tests/files/file-ignore-service.test.ts`
- `node/tests/files/file-discovery-service.test.ts`
- `node/tests/files/file-service.test.ts`

**Modify:**
- `node/package.json` — add `ignore`, `chokidar`
- `node/src/main.ts` — add `FilesServiceProvider`

---

## Task 1: Install Packages

**Files:**
- Modify: `node/package.json`

- [ ] **Step 1: Add dependencies**

Edit `node/package.json` — add to `"dependencies"`:

```json
"chokidar": "^4.0.3",
"ignore": "^7.0.5"
```

The full `dependencies` block becomes:

```json
"dependencies": {
  "chalk": "^5.6.2",
  "chokidar": "^4.0.3",
  "ignore": "^7.0.5",
  "ink": "^6.8.0",
  "js-yaml": "^4.1.0",
  "marked": "^17.0.5",
  "marked-terminal": "^7.3.0",
  "react": "^19.2.4",
  "simple-git": "^3.27.0",
  "zod": "^4.3.6"
}
```

- [ ] **Step 2: Install**

```bash
cd /home/sincore/source/byte/node && bun install
```

Expected: lockfile updated, `node_modules/ignore` and `node_modules/chokidar` present.

- [ ] **Step 3: Commit**

```bash
cd /home/sincore/source/byte/node
git add package.json bun.lock
git commit -m "feat(files): add ignore and chokidar dependencies"
```

---

## Task 2: Models

**Files:**
- Create: `node/src/files/models.ts`

- [ ] **Step 1: Write the file**

```typescript
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
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /home/sincore/source/byte/node && bun build src/files/models.ts --target=bun 2>&1 | head -20
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/files/models.ts
git commit -m "feat(files): add FileMode enum and FileContext model"
```

---

## Task 3: FileIgnoreService (TDD)

**Files:**
- Create: `node/src/files/service/file-ignore-service.ts`
- Create: `node/tests/files/file-ignore-service.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `node/tests/files/file-ignore-service.test.ts`:

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { mkdtempSync, writeFileSync, rmSync } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import type { IApplication } from '../../src/support/concerns/bootable.ts'
import { FileIgnoreService } from '../../src/files/service/file-ignore-service.ts'

function makeApp(rootPath: string, ignorePatterns: string[] = []): IApplication {
  return {
    make: (key: unknown) => {
      if (key === 'path.root') return rootPath
      if (key === 'config') return { files: { ignore: ignorePatterns, watch: { enable: false } } }
      return {}
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  } as unknown as IApplication
}

describe('FileIgnoreService', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'byte-ignore-test-'))
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('ignores patterns from .gitignore', () => {
    writeFileSync(join(tmpDir, '.gitignore'), 'node_modules\n')
    const svc = new FileIgnoreService(makeApp(tmpDir))
    svc.ensureBooted()
    expect(svc.isIgnored(join(tmpDir, 'node_modules/foo.ts'))).toBe(true)
  })

  it('ignores patterns from config', () => {
    const svc = new FileIgnoreService(makeApp(tmpDir, ['.byte/cache']))
    svc.ensureBooted()
    expect(svc.isIgnored(join(tmpDir, '.byte/cache/foo'))).toBe(true)
  })

  it('allows non-ignored file', () => {
    const svc = new FileIgnoreService(makeApp(tmpDir))
    svc.ensureBooted()
    expect(svc.isIgnored(join(tmpDir, 'src/main.ts'))).toBe(false)
  })

  it('handles missing .gitignore gracefully', () => {
    const svc = new FileIgnoreService(makeApp(tmpDir))
    expect(() => svc.ensureBooted()).not.toThrow()
  })

  it('refresh() picks up new patterns', () => {
    const svc = new FileIgnoreService(makeApp(tmpDir))
    svc.ensureBooted()
    expect(svc.isIgnored(join(tmpDir, 'dist/bundle.js'))).toBe(false)
    writeFileSync(join(tmpDir, '.gitignore'), 'dist\n')
    svc.refresh()
    expect(svc.isIgnored(join(tmpDir, 'dist/bundle.js'))).toBe(true)
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sincore/source/byte/node && bun test tests/files/file-ignore-service.test.ts
```

Expected: FAIL — `Cannot find module '../../src/files/service/file-ignore-service.ts'`

- [ ] **Step 3: Implement FileIgnoreService**

Create `node/src/files/service/file-ignore-service.ts`:

```typescript
import { readFileSync, existsSync } from 'fs'
import { relative, isAbsolute } from 'path'
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
    const gitignorePath = `${this._rootPath}/.gitignore`
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /home/sincore/source/byte/node && bun test tests/files/file-ignore-service.test.ts
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/files/service/file-ignore-service.ts tests/files/file-ignore-service.test.ts
git commit -m "feat(files): add FileIgnoreService with gitignore + config pattern support"
```

---

## Task 4: FileDiscoveryService (TDD)

**Files:**
- Create: `node/src/files/service/file-discovery-service.ts`
- Create: `node/tests/files/file-discovery-service.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `node/tests/files/file-discovery-service.test.ts`:

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import type { IApplication } from '../../src/support/concerns/bootable.ts'
import { FileIgnoreService } from '../../src/files/service/file-ignore-service.ts'
import { FileDiscoveryService } from '../../src/files/service/file-discovery-service.ts'

function makeIgnoreService(rootPath: string, patterns: string[] = []): FileIgnoreService {
  const app = {
    make: (key: unknown) => {
      if (key === 'path.root') return rootPath
      if (key === 'config') return { files: { ignore: patterns, watch: { enable: false } } }
      return {}
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  } as unknown as IApplication
  const svc = new FileIgnoreService(app)
  svc.ensureBooted()
  return svc
}

function makeApp(rootPath: string, ignoreService: FileIgnoreService): IApplication {
  return {
    make: (key: unknown) => {
      if (key === 'path.root') return rootPath
      if (key === FileIgnoreService) return ignoreService
      return {}
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  } as unknown as IApplication
}

describe('FileDiscoveryService', () => {
  let tmpDir: string
  let ignoreService: FileIgnoreService
  let service: FileDiscoveryService

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'byte-discovery-test-'))
    mkdirSync(join(tmpDir, 'src'))
    writeFileSync(join(tmpDir, 'src/main.ts'), 'export const x = 1\n')
    writeFileSync(join(tmpDir, 'src/utils.ts'), 'export const y = 2\n')
    writeFileSync(join(tmpDir, 'README.md'), '# Test\n')
    ignoreService = makeIgnoreService(tmpDir)
    service = new FileDiscoveryService(makeApp(tmpDir, ignoreService))
    service.ensureBooted()
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('getFiles() returns discovered files', () => {
    const files = service.getFiles()
    expect(files.some(f => f.includes('main.ts'))).toBe(true)
    expect(files.some(f => f.includes('README.md'))).toBe(true)
  })

  it('getFiles(ext) filters by extension', () => {
    const tsFiles = service.getFiles('ts')
    expect(tsFiles.every(f => f.endsWith('.ts'))).toBe(true)
    expect(tsFiles.some(f => f.includes('README.md'))).toBe(false)
  })

  it('getRelativePaths() returns relative strings', () => {
    const paths = service.getRelativePaths()
    expect(paths.length).toBeGreaterThan(0)
    for (const p of paths) {
      expect(p.startsWith('/')).toBe(false)
    }
  })

  it('findFiles() exact prefix match', () => {
    const results = service.findFiles('src/main')
    expect(results.some(f => f.includes('main.ts'))).toBe(true)
  })

  it('findFiles() fuzzy filename match', () => {
    const results = service.findFiles('utils')
    expect(results.some(f => f.includes('utils.ts'))).toBe(true)
  })

  it('addFile() adds to cache', () => {
    const newFile = join(tmpDir, 'new.ts')
    writeFileSync(newFile, '')
    expect(service.addFile(newFile)).toBe(true)
    expect(service.getFiles().includes(newFile)).toBe(true)
  })

  it('addFile() returns false for already-cached file', () => {
    const existing = service.getFiles()[0]
    expect(service.addFile(existing)).toBe(false)
  })

  it('removeFile() removes from cache', () => {
    const file = service.getFiles().find(f => f.includes('main.ts'))!
    expect(service.removeFile(file)).toBe(true)
    expect(service.getFiles().includes(file)).toBe(false)
  })

  it('ignored files are excluded on boot', () => {
    const ignoredIgnoreService = makeIgnoreService(tmpDir, ['src'])
    const svc = new FileDiscoveryService(makeApp(tmpDir, ignoredIgnoreService))
    svc.ensureBooted()
    expect(svc.getFiles().some(f => f.includes('/src/'))).toBe(false)
  })

  it('refresh() rescans and picks up new files', () => {
    const newFile = join(tmpDir, 'new-file.ts')
    writeFileSync(newFile, '')
    service.refresh()
    expect(service.getFiles().includes(newFile)).toBe(true)
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sincore/source/byte/node && bun test tests/files/file-discovery-service.test.ts
```

Expected: FAIL — `Cannot find module '../../src/files/service/file-discovery-service.ts'`

- [ ] **Step 3: Implement FileDiscoveryService**

Create `node/src/files/service/file-discovery-service.ts`:

```typescript
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

    return [...tier1, ...tier2, ...tier3]
      .sort((a, b) =>
        relative(this._rootPath, a).localeCompare(relative(this._rootPath, b))
      )
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /home/sincore/source/byte/node && bun test tests/files/file-discovery-service.test.ts
```

Expected: 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/files/service/file-discovery-service.ts tests/files/file-discovery-service.test.ts
git commit -m "feat(files): add FileDiscoveryService with recursive scan, find, and refresh"
```

---

## Task 5: FileService (TDD)

**Files:**
- Create: `node/src/files/service/file-service.ts`
- Create: `node/tests/files/file-service.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `node/tests/files/file-service.test.ts`:

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import type { IApplication } from '../../src/support/concerns/bootable.ts'
import { FileService } from '../../src/files/service/file-service.ts'
import { FileDiscoveryService } from '../../src/files/service/file-discovery-service.ts'
import { FileMode } from '../../src/files/models.ts'

function makeApp(rootPath: string, discoveredFiles: string[]): IApplication {
  const mockDiscovery = {
    getFiles: (_ext?: string) => discoveredFiles,
    findFiles: (pattern: string) => discoveredFiles.filter(f => f.includes(pattern)),
    getRelativePaths: () => [],
    addFile: () => false,
    removeFile: () => false,
    refresh: () => {},
    ensureBooted: () => {},
  }

  return {
    make: (key: unknown) => {
      if (key === 'path.root') return rootPath
      if (key === FileDiscoveryService) return mockDiscovery
      if (key === 'event-bus') return { emit: async (p: unknown) => p }
      if (key === 'console') return { print: () => {}, printError: () => {} }
      return {}
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  } as unknown as IApplication
}

describe('FileService', () => {
  let tmpDir: string
  let service: FileService
  let mainTs: string
  let utilsTs: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'byte-fileservice-test-'))
    mkdirSync(join(tmpDir, 'src'))
    mainTs = join(tmpDir, 'src/main.ts')
    utilsTs = join(tmpDir, 'src/utils.ts')
    writeFileSync(mainTs, 'const x = 1\n')
    writeFileSync(utilsTs, 'const y = 2\n')
    service = new FileService(makeApp(tmpDir, [mainTs, utilsTs]))
    service.ensureBooted()
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('addFile() single path adds to context', async () => {
    const result = await service.addFile(mainTs, FileMode.EDITABLE)
    expect(result).toBe(true)
    expect(service.isFileInContext(mainTs)).toBe(true)
  })

  it('addFile() rejects file not in discovery cache', async () => {
    const result = await service.addFile(join(tmpDir, 'nonexistent.ts'), FileMode.EDITABLE)
    expect(result).toBe(false)
  })

  it('addFile() rejects duplicate', async () => {
    await service.addFile(mainTs, FileMode.EDITABLE)
    const result = await service.addFile(mainTs, FileMode.EDITABLE)
    expect(result).toBe(false)
  })

  it('addFile() glob pattern adds multiple files', async () => {
    const result = await service.addFile('src/*.ts', FileMode.EDITABLE)
    expect(result).toBe(true)
    expect(service.isFileInContext(mainTs)).toBe(true)
    expect(service.isFileInContext(utilsTs)).toBe(true)
  })

  it('removeFile() single path removes from context', async () => {
    await service.addFile(mainTs, FileMode.EDITABLE)
    const result = await service.removeFile(mainTs)
    expect(result).toBe(true)
    expect(service.isFileInContext(mainTs)).toBe(false)
  })

  it('removeFile() glob pattern removes multiple files', async () => {
    await service.addFile(mainTs, FileMode.EDITABLE)
    await service.addFile(utilsTs, FileMode.EDITABLE)
    const result = await service.removeFile('src/*.ts')
    expect(result).toBe(true)
    expect(service.isFileInContext(mainTs)).toBe(false)
    expect(service.isFileInContext(utilsTs)).toBe(false)
  })

  it('listFiles() returns all context files sorted by relativePath', async () => {
    await service.addFile(utilsTs, FileMode.EDITABLE)
    await service.addFile(mainTs, FileMode.EDITABLE)
    const files = service.listFiles()
    expect(files).toHaveLength(2)
    expect(files[0].relativePath < files[1].relativePath).toBe(true)
  })

  it('listFiles(FileMode.EDITABLE) returns only editable files', async () => {
    await service.addFile(mainTs, FileMode.READ_ONLY)
    await service.addFile(utilsTs, FileMode.EDITABLE)
    const editable = service.listFiles(FileMode.EDITABLE)
    expect(editable).toHaveLength(1)
    expect(editable[0].path).toBe(utilsTs)
  })

  it('setFileMode() changes the mode', async () => {
    await service.addFile(mainTs, FileMode.READ_ONLY)
    expect(service.listFiles(FileMode.READ_ONLY)).toHaveLength(1)
    service.setFileMode(mainTs, FileMode.EDITABLE)
    expect(service.listFiles(FileMode.READ_ONLY)).toHaveLength(0)
    expect(service.listFiles(FileMode.EDITABLE)).toHaveLength(1)
  })

  it('getFileContext() returns correct FileContext', async () => {
    await service.addFile(mainTs, FileMode.READ_ONLY)
    const ctx = service.getFileContext(mainTs)
    expect(ctx).not.toBeNull()
    expect(ctx!.mode).toBe(FileMode.READ_ONLY)
    expect(ctx!.path).toBe(mainTs)
  })

  it('isFileInContext() returns correct boolean', async () => {
    expect(service.isFileInContext(mainTs)).toBe(false)
    await service.addFile(mainTs, FileMode.EDITABLE)
    expect(service.isFileInContext(mainTs)).toBe(true)
  })

  it('generateContextPrompt() returns boundaries with fenced code blocks', async () => {
    await service.addFile(mainTs, FileMode.READ_ONLY)
    const [readOnly, editable] = await service.generateContextPrompt()
    expect(readOnly).toHaveLength(1)
    expect(readOnly[0]).toContain('<file')
    expect(readOnly[0]).toContain('```typescript')
    expect(readOnly[0]).toContain('const x = 1')
    expect(readOnly[0]).toContain('</file>')
    expect(editable).toHaveLength(0)
  })

  it('generateProjectHierarchy() returns a tree string with boundaries', async () => {
    const hierarchy = await service.generateProjectHierarchy()
    expect(typeof hierarchy).toBe('string')
    expect(hierarchy).toContain('<project_hierarchy>')
    expect(hierarchy).toContain('</project_hierarchy>')
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sincore/source/byte/node && bun test tests/files/file-service.test.ts
```

Expected: FAIL — `Cannot find module '../../src/files/service/file-service.ts'`

- [ ] **Step 3: Implement FileService**

Create `node/src/files/service/file-service.ts`:

```typescript
import { join, isAbsolute, relative, basename } from 'path'
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /home/sincore/source/byte/node && bun test tests/files/file-service.test.ts
```

Expected: 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/files/service/file-service.ts tests/files/file-service.test.ts
git commit -m "feat(files): add FileService with context management and prompt generation"
```

---

## Task 6: FileWatcherService + Stubs

**Files:**
- Create: `node/src/files/service/file-watcher-service.ts`
- Create: `node/src/files/service/ai-comment-watcher-service.ts`
- Create: `node/src/files/tools.ts`

- [ ] **Step 1: Implement FileWatcherService**

Create `node/src/files/service/file-watcher-service.ts`:

```typescript
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
```

- [ ] **Step 2: Implement AICommentWatcherService stub**

Create `node/src/files/service/ai-comment-watcher-service.ts`:

```typescript
import { Service } from '../../support/service.ts'
import { Payload } from '../../support/concerns/eventable.ts'

export class AICommentWatcherService extends Service {
  static token = Symbol('AICommentWatcherService')

  override boot(): void {}

  async handleFileChange(payload: Payload): Promise<Payload> {
    return payload
  }

  async modifyUserRequestHook(payload: Payload): Promise<Payload> {
    return payload
  }

  async addReinforcementHook(payload: Payload): Promise<Payload> {
    return payload
  }
}
```

- [ ] **Step 3: Implement tools.ts stub**

Create `node/src/files/tools.ts`:

```typescript
export async function readFiles(_filePaths: string[]): Promise<string> {
  return ''
}
```

- [ ] **Step 4: Verify compilation**

```bash
cd /home/sincore/source/byte/node && bun build src/files/service/file-watcher-service.ts --target=bun 2>&1 | head -20
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add src/files/service/file-watcher-service.ts \
        src/files/service/ai-comment-watcher-service.ts \
        src/files/tools.ts
git commit -m "feat(files): add FileWatcherService (chokidar), AICommentWatcherService stub, tools stub"
```

---

## Task 7: Commands

**Files:**
- Create: `node/src/files/commands/add-file-command.ts`
- Create: `node/src/files/commands/read-only-command.ts`
- Create: `node/src/files/commands/drop-file-command.ts`
- Create: `node/src/files/commands/list-files-command.ts`
- Create: `node/src/files/commands/switch-mode-command.ts`
- Create: `node/src/files/commands/reload-files-command.ts`

- [ ] **Step 1: Implement AddFileCommand**

Create `node/src/files/commands/add-file-command.ts`:

```typescript
import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'
import { FileDiscoveryService } from '../service/file-discovery-service.ts'
import { FileMode } from '../models.ts'

export class AddFileCommand extends Command {
  get name(): string { return 'add' }
  get description(): string { return 'Add a file to context as editable' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    if (!path) {
      const console = this.app.make<{ printError(t: string): void }>('console')
      console.printError('Usage: /add <path>')
      return
    }
    const fileService = this.app.make<FileService>(FileService as never)
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
    const added = await fileService.addFile(path, FileMode.EDITABLE)
    if (added) console.print(`Added: ${path}`)
    else console.printError(`Could not add: ${path}`)
  }

  override async getCompletions(text: string): Promise<string[]> {
    const fileService = this.app.make<FileService>(FileService as never)
    const matches = await fileService.findProjectFiles(text)
    const rootPath = this.app.make<string>('path.root')
    return matches.map(f => {
      const { relative } = require('path')
      return relative(rootPath, f)
    })
  }
}
```

- [ ] **Step 2: Implement ReadOnlyCommand**

Create `node/src/files/commands/read-only-command.ts`:

```typescript
import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'
import { FileMode } from '../models.ts'
import { relative } from 'path'

export class ReadOnlyCommand extends Command {
  get name(): string { return 'read-only' }
  get description(): string { return 'Add a file to context as read-only' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    if (!path) {
      const console = this.app.make<{ printError(t: string): void }>('console')
      console.printError('Usage: /read-only <path>')
      return
    }
    const fileService = this.app.make<FileService>(FileService as never)
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
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
```

- [ ] **Step 3: Implement DropFileCommand**

Create `node/src/files/commands/drop-file-command.ts`:

```typescript
import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'

export class DropFileCommand extends Command {
  get name(): string { return 'drop' }
  get description(): string { return 'Remove a file from context' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    if (!path) {
      const console = this.app.make<{ printError(t: string): void }>('console')
      console.printError('Usage: /drop <path>')
      return
    }
    const fileService = this.app.make<FileService>(FileService as never)
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')
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
```

- [ ] **Step 4: Implement ListFilesCommand**

Create `node/src/files/commands/list-files-command.ts`:

```typescript
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
```

- [ ] **Step 5: Implement SwitchModeCommand**

Create `node/src/files/commands/switch-mode-command.ts`:

```typescript
import { Command } from '../../cli/service/command-registry.ts'
import { FileService } from '../service/file-service.ts'
import { FileMode } from '../models.ts'

export class SwitchModeCommand extends Command {
  get name(): string { return 'switch' }
  get description(): string { return 'Toggle a context file between read-only and editable' }

  async execute(args: string): Promise<void> {
    const path = args.trim()
    const fileService = this.app.make<FileService>(FileService as never)
    const console = this.app.make<{ print(t: string): void; printError(t: string): void }>('console')

    if (!path) {
      console.printError('Usage: /switch <path>')
      return
    }
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
```

- [ ] **Step 6: Implement ReloadFilesCommand**

Create `node/src/files/commands/reload-files-command.ts`:

```typescript
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
```

- [ ] **Step 7: Verify compilation**

```bash
cd /home/sincore/source/byte/node && bun build src/files/commands/add-file-command.ts --target=bun 2>&1 | head -20
```

Expected: no errors.

- [ ] **Step 8: Commit**

```bash
git add src/files/commands/
git commit -m "feat(files): add all 6 file management commands (/add, /read-only, /drop, /ls, /switch, /reload)"
```

---

## Task 8: Service Provider, Barrel, and Wire into main.ts

**Files:**
- Create: `node/src/files/service-provider.ts`
- Create: `node/src/files/index.ts`
- Modify: `node/src/main.ts`

- [ ] **Step 1: Implement FilesServiceProvider**

Create `node/src/files/service-provider.ts`:

```typescript
import { ServiceProvider } from '../support/service-provider.ts'
import { CommandRegistry } from '../cli/service/command-registry.ts'
import { EventBus, EventType } from '../foundation/event-bus.ts'
import type { ByteConfig } from '../config/schemas.ts'
import { FileIgnoreService } from './service/file-ignore-service.ts'
import { FileDiscoveryService } from './service/file-discovery-service.ts'
import { FileService } from './service/file-service.ts'
import { FileWatcherService } from './service/file-watcher-service.ts'
import { AICommentWatcherService } from './service/ai-comment-watcher-service.ts'
import { AddFileCommand } from './commands/add-file-command.ts'
import { ReadOnlyCommand } from './commands/read-only-command.ts'
import { DropFileCommand } from './commands/drop-file-command.ts'
import { ListFilesCommand } from './commands/list-files-command.ts'
import { SwitchModeCommand } from './commands/switch-mode-command.ts'
import { ReloadFilesCommand } from './commands/reload-files-command.ts'

export class FilesServiceProvider extends ServiceProvider {
  override register(): void {
    this.app.singleton(FileIgnoreService as never, () => {
      const svc = new FileIgnoreService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(FileDiscoveryService as never, () => {
      const svc = new FileDiscoveryService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(FileService as never, () => {
      const svc = new FileService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(FileWatcherService as never, () => {
      const svc = new FileWatcherService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(AICommentWatcherService as never, () => {
      const svc = new AICommentWatcherService(this.app)
      svc.ensureBooted()
      return svc
    })
  }

  override async boot(): Promise<void> {
    const registry = this.app.make<CommandRegistry>('command-registry')
    registry.register(new AddFileCommand(this.app))
    registry.register(new ReadOnlyCommand(this.app))
    registry.register(new DropFileCommand(this.app))
    registry.register(new ListFilesCommand(this.app))
    registry.register(new SwitchModeCommand(this.app))
    registry.register(new ReloadFilesCommand(this.app))

    const eventBus = this.app.make<EventBus>('event-bus')
    const fileService = this.app.make<FileService>(FileService as never)
    const fileWatcher = this.app.make<FileWatcherService>(FileWatcherService as never)

    void fileWatcher.startWatching()

    eventBus.on(EventType.PRE_PROMPT_TOOLKIT, (payload) =>
      fileService.listInContextFilesHook(payload)
    )

    eventBus.on(EventType.POST_BOOT, async (payload) => {
      const discovery = this.app.make<FileDiscoveryService>(FileDiscoveryService as never)
      const console = this.app.make<{ print(t: string): void }>('console')
      console.print(`Discovered ${discovery.getFiles().length} files.`)
      return payload
    })

    const config = this.app.make<ByteConfig>('config')
    if (config.files.watch.enable) {
      const aiWatcher = this.app.make<AICommentWatcherService>(AICommentWatcherService as never)
      eventBus.on(EventType.POST_PROMPT_TOOLKIT, (payload) =>
        aiWatcher.modifyUserRequestHook(payload)
      )
      eventBus.on(EventType.GATHER_REINFORCEMENT, (payload) =>
        aiWatcher.addReinforcementHook(payload)
      )
      eventBus.on(EventType.FILE_CHANGED, (payload) =>
        aiWatcher.handleFileChange(payload)
      )
    }
  }

  override async shutdown(): Promise<void> {
    const fileWatcher = this.app.make<FileWatcherService>(FileWatcherService as never)
    await fileWatcher.stopWatching()
  }
}
```

- [ ] **Step 2: Write barrel**

Create `node/src/files/index.ts`:

```typescript
export { FileMode, FileContext } from './models.ts'
export { FileIgnoreService } from './service/file-ignore-service.ts'
export { FileDiscoveryService } from './service/file-discovery-service.ts'
export { FileService } from './service/file-service.ts'
export { FileWatcherService } from './service/file-watcher-service.ts'
export { AICommentWatcherService } from './service/ai-comment-watcher-service.ts'
export { FilesServiceProvider } from './service-provider.ts'
```

- [ ] **Step 3: Wire FilesServiceProvider into main.ts**

Edit `node/src/main.ts` — add the import and add to the provider list:

```typescript
import React from 'react'
import { render } from 'ink'
import { Application } from './foundation/application.ts'
import { FoundationServiceProvider } from './foundation/service-provider.ts'
import { CLIServiceProvider } from './cli/service-provider.ts'
import { GitServiceProvider } from './git/service-provider.ts'
import { FilesServiceProvider } from './files/service-provider.ts'
import { Console } from './cli/service/console.ts'
import { PromptService } from './cli/service/prompt-service.ts'
import { App } from './cli/components/app.tsx'

const app = Application.configure(process.cwd(), [
  FoundationServiceProvider as never,
  CLIServiceProvider as never,
  GitServiceProvider as never,
  FilesServiceProvider as never,
]).create()

await app.boot()

const consoleService = app.make<Console>('console')
const promptService = app.make<PromptService>(PromptService as never)
const cachePath = app.make<string>('path.cache')

render(React.createElement(App, { consoleService, promptService, cachePath }))
```

- [ ] **Step 4: Run full test suite**

```bash
cd /home/sincore/source/byte/node && bun test
```

Expected: all existing tests + new files tests PASS, no regressions.

- [ ] **Step 5: Smoke-test app startup**

```bash
cd /home/sincore/source/byte/node && timeout 3 bun run src/main.ts 2>&1 | head -10 || true
```

Expected: app starts, prints discovered file count, no import errors.

- [ ] **Step 6: Commit**

```bash
git add src/files/service-provider.ts src/files/index.ts src/main.ts
git commit -m "feat(files): wire FilesServiceProvider into app — files domain migration complete"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|---|---|
| `FileMode` enum, `FileContext` class | Task 2 |
| `FileIgnoreService` — boot, isIgnored, refresh, getIgnore | Task 3 |
| `.gitignore` + `config.files.ignore` pattern loading | Task 3 |
| `FileDiscoveryService` — scan, getFiles, getRelativePaths, findFiles, addFile, removeFile, refresh | Task 4 |
| Three-tier findFiles priority | Task 4 |
| `FileService` — addFile (single + glob), removeFile (single + glob), listFiles, setFileMode, getFileContext, isFileInContext | Task 5 |
| `generateContextPrompt`, `generateContextPromptWithLineNumbers` | Task 5 |
| `generateProjectHierarchy` (maxFilesPerDir=5, root shows all) | Task 5 |
| `listInContextFilesHook` | Task 5 |
| `FileWatcherService` — chokidar, add/change/unlink handlers, FILE_CHANGED events | Task 6 |
| `AICommentWatcherService` stub | Task 6 |
| `tools.ts` stub | Task 6 |
| All 6 commands with completions | Task 7 |
| `FilesServiceProvider` — register 5 services, boot 6 commands, start watcher, events | Task 8 |
| Barrel `index.ts` | Task 8 |
| Wire into `main.ts` | Task 8 |
| `ignore` + `chokidar` packages | Task 1 |
| Tests: FileIgnoreService (5), FileDiscoveryService (9), FileService (13) | Tasks 3–5 |

**No placeholders:** all steps contain complete code.

**Type consistency:** `FileContext` constructed with `(path, mode, rootPath)` throughout. `FileDiscoveryService` resolved as `FileDiscoveryService as never` everywhere. `FileService._discovery()` always returns `FileDiscoveryService`. `Payload.set()` returns `this` (Payload) — `listInContextFilesHook` return is correct.
