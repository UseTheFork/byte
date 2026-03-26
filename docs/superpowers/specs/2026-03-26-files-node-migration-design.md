# Design: Files Domain — Python to Node/TS Migration

**Date:** 2026-03-26
**Branch:** dev-v3-node
**Scope:** `files` domain — models, `FileIgnoreService`, `FileDiscoveryService`, `FileService`, `FileWatcherService`, `AICommentWatcherService` stub, 6 commands, `tools.ts` stub, `FilesServiceProvider`. Python source is preserved and serves as the reference implementation.

---

## Overview

Port the files layer of the byte CLI from Python (pathspec + watchfiles) to TypeScript (ignore + chokidar), running under Bun. After this migration, `FileIgnoreService` manages gitignore pattern matching, `FileDiscoveryService` maintains a cached index of project files, `FileService` manages the set of files in AI context and generates prompts, and `FileWatcherService` keeps the cache up-to-date via chokidar. `AICommentWatcherService` is a stub pending agent domain migration. All 6 file management commands are fully implemented.

---

## New Packages

Add to `node/package.json` dependencies:
- `ignore` — gitignore-style pattern matching (replaces Python `pathspec`)
- `chokidar` — file system watching (replaces Python `watchfiles`)

---

## Repository Layout

```
node/src/files/
  index.ts                          ← barrel
  models.ts                         ← FileMode enum, FileContext class
  service-provider.ts               ← FilesServiceProvider
  tools.ts                          ← readFiles stub
  service/
    file-ignore-service.ts
    file-discovery-service.ts
    file-service.ts
    file-watcher-service.ts
    ai-comment-watcher-service.ts   ← stub

node/tests/files/
  file-ignore-service.test.ts
  file-discovery-service.test.ts
  file-service.test.ts
```

**Modified files:**
- `node/package.json` — add `ignore`, `chokidar`
- `node/src/main.ts` — add `FilesServiceProvider` to provider list

---

## Architecture

### Models (`models.ts`)

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
    public readonly path:     string,   // absolute path
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

Key differences from Python:
- `path` is `string` (not `Path`) — consistent with Node path handling
- `getContent()` returns `null` on error (callers handle null; Python's error string is dropped)
- Uses `getLanguageFromFilename` from existing `node/src/support/utils/`

---

### `FileIgnoreService` (`service/file-ignore-service.ts`)

Wraps the `ignore` package. Loads `.gitignore` + `config.files.ignore` patterns on `boot()`. All methods are synchronous — required because `FileWatcherService` uses `isIgnored()` as a chokidar filter callback.

```typescript
class FileIgnoreService extends Service {
  static token = Symbol('FileIgnoreService')
  private _ig!: Ignore

  async boot(): Promise<void> { this._loadIgnorePatterns() }

  isIgnored(path: string): boolean   // relative or absolute path
  refresh(): void                    // reloads patterns from disk + config
  getIgnore(): Ignore                // for advanced use by FileWatcherService
}
```

Pattern loading:
1. Read `.gitignore` from project root if it exists
2. Append `config.files.ignore` patterns
3. Compile into `ignore()` instance

`isIgnored()` converts absolute paths to relative (from project root) before testing, consistent with git behaviour. Returns `true` if path is outside project root.

---

### `FileDiscoveryService` (`service/file-discovery-service.ts`)

Walks the project tree on `boot()` using `fs.readdirSync` recursively, caching results in `_allFiles: Set<string>` (absolute path strings). Depends on `FileIgnoreService`.

```typescript
class FileDiscoveryService extends Service {
  static token = Symbol('FileDiscoveryService')
  private _allFiles: Set<string> = new Set()

  async boot(): Promise<void> { this._scanProjectFiles() }

  getFiles(extension?: string): string[]
  getRelativePaths(extension?: string): string[]
  findFiles(pattern: string): string[]   // fuzzy: exact prefix → filename → path
  addFile(path: string): boolean
  removeFile(path: string): boolean
  refresh(): void                        // clears cache, refreshes ignore, rescans
}
```

`_scanProjectFiles()` — synchronous recursive walk:
- Skip ignored directories early (prunes traversal)
- Add non-ignored files to `_allFiles`

`findFiles(pattern)` — three-tier priority:
1. Relative path starts with pattern (exact prefix)
2. Pattern appears in filename
3. Pattern appears anywhere in relative path

Results are sorted by relative path.

---

### `FileService` (`service/file-service.ts`)

Manages `_contextFiles: Map<string, FileContext>` (keyed by absolute path). Resolves `FileDiscoveryService` lazily inside methods.

```typescript
class FileService extends Service {
  static token = Symbol('FileService')
  private _contextFiles: Map<string, FileContext> = new Map()

  async boot(): Promise<void> {}   // initialises empty map

  async addFile(path: string, mode: FileMode): Promise<boolean>
  async removeFile(path: string): Promise<boolean>
  listFiles(mode?: FileMode): FileContext[]
  setFileMode(path: string, mode: FileMode): boolean
  getFileContext(path: string): FileContext | null
  isFileInContext(path: string): boolean
  async getProjectFiles(extension?: string): Promise<string[]>
  async findProjectFiles(pattern: string): Promise<string[]>
  clearContext(): void
  async generateContextPrompt(): Promise<[string[], string[]]>
  async generateContextPromptWithLineNumbers(): Promise<[string[], string[]]>
  async generateProjectHierarchy(): Promise<string>
  async listInContextFilesHook(payload: Payload): Promise<Payload>
}
```

**`addFile(path, mode)`:**
- Supports glob patterns via `Bun.Glob` (detected by presence of `*`, `?`, `[`)
- Relative paths resolved from `app.rootPath()`
- Only adds files present in `FileDiscoveryService` cache
- Single file: returns `false` if already in context or not discovered
- Glob: returns `true` if at least one file was added
- Emits `FILE_ADDED` event on single-file success

**`removeFile(path)`:**
- Supports glob patterns (matched against current context keys)
- Returns `false` if no files removed

**`listFiles(mode?)`** — returns array sorted by `relativePath`

**`generateContextPrompt()`** — formats each file with `Boundary.open/close` + language fenced code block, returning `[readOnlyList, editableList]`

**`generateContextPromptWithLineNumbers()`** — same but prepends `   N | ` to each line (1-indexed)

**`generateProjectHierarchy()`** — recursive tree builder using `FileDiscoveryService.getFiles()` (not the internal `_allFiles` set):
- Shows up to `maxFilesPerDir` (default 5) files per directory, with `... N more files` message
- Root level shows all files
- Filters directories that contain no discovered files

**`listInContextFilesHook(payload)`** — reads `info_panel` from payload, appends read-only and editable file panels as plain text lists, returns updated payload

---

### `FileWatcherService` (`service/file-watcher-service.ts`)

Wraps chokidar. Started via `app.booted()` hook in the provider.

```typescript
class FileWatcherService extends Service {
  static token = Symbol('FileWatcherService')

  async boot(): Promise<void> {}
  async startWatching(): Promise<void>
}
```

**`startWatching()`:**
- Resolves `FileIgnoreService`, `FileDiscoveryService`, `FileService`
- Creates chokidar watcher: `chokidar.watch(rootPath, { ignored: (path) => ignoreService.isIgnored(path), persistent: true, ignoreInitial: true })`
- `add` → `fileDiscovery.addFile(path)`
- `unlink` → `fileDiscovery.removeFile(path)` + if in context, `fileService.removeFile(path)`
- `add`/`change`/`unlink` → emits `FILE_CHANGED` payload with `{ file_path, change_type }`
- Registers the watcher with `TaskManager` so it shuts down cleanly

---

### `AICommentWatcherService` (`service/ai-comment-watcher-service.ts`) — stub

```typescript
export class AICommentWatcherService extends Service {
  static token = Symbol('AICommentWatcherService')
  async boot(): Promise<void> {}
  async handleFileChange(payload: Payload): Promise<Payload> { return payload }
  async modifyUserRequestHook(payload: Payload): Promise<Payload> { return payload }
  async addReinforcementHook(payload: Payload): Promise<Payload> { return payload }
}
```

Pending: depends on `AskAgent` / `CoderAgent` (agent domain not yet migrated).

---

### `tools.ts` — stub

```typescript
export async function readFiles(_filePaths: string[]): Promise<string> {
  return ''
}
```

Pending: depends on tools/agent system.

---

### Commands

All 6 commands extend `Command` and implement `execute(args: string): Promise<void>`. Argument parsing is `args.trim()` (each command takes at most one file path).

| Class | Command | Behaviour |
|---|---|---|
| `AddFileCommand` | `/add` | `fileService.addFile(args, FileMode.EDITABLE)` |
| `ReadOnlyCommand` | `/read-only` | `fileService.addFile(args, FileMode.READ_ONLY)` |
| `DropFileCommand` | `/drop` | `fileService.removeFile(args)` |
| `ListFilesCommand` | `/ls` | prints read-only + editable file lists |
| `SwitchModeCommand` | `/switch` | reads current mode via `getFileContext()`, toggles via `setFileMode()` |
| `ReloadFilesCommand` | `/reload` | calls `fileDiscovery.refresh()` |

`AddFileCommand`, `ReadOnlyCommand`, `DropFileCommand`, and `SwitchModeCommand` implement `getCompletions(text)` delegating to `FileService`.

---

### `FilesServiceProvider` (`service-provider.ts`)

```typescript
export class FilesServiceProvider extends ServiceProvider {
  override register(): void {
    // singleton registrations for all 5 services
  }

  override async boot(): Promise<void> {
    // 1. Register 6 commands with CommandRegistry
    // 2. Start FileWatcherService via app.booted()
    // 3. eventBus.on(PRE_PROMPT_TOOLKIT) → fileService.listInContextFilesHook
    // 4. eventBus.on(POST_BOOT) → show discovered file count
    // 5. If config.files.watch.enable:
    //    - eventBus.on(POST_PROMPT_TOOLKIT) → aiWatcher.modifyUserRequestHook
    //    - eventBus.on(GATHER_REINFORCEMENT) → aiWatcher.addReinforcementHook
    //    - eventBus.on(FILE_CHANGED) → aiWatcher.handleFileChange
  }
}
```

`FilesServiceProvider` is added to the provider list in `main.ts` alongside `GitServiceProvider`.

---

### Barrel (`index.ts`)

```typescript
export { FileMode, FileContext } from './models.ts'
export { FileIgnoreService } from './service/file-ignore-service.ts'
export { FileDiscoveryService } from './service/file-discovery-service.ts'
export { FileService } from './service/file-service.ts'
export { FileWatcherService } from './service/file-watcher-service.ts'
export { AICommentWatcherService } from './service/ai-comment-watcher-service.ts'
export { FilesServiceProvider } from './service-provider.ts'
```

---

## Testing

**`file-ignore-service.test.ts`** — real temp directory, no mocking.

| Test | Verifies |
|---|---|
| ignores pattern from `.gitignore` | `node_modules/foo.ts` → ignored |
| ignores pattern from config | `.byte/cache/foo` → ignored |
| allows non-ignored file | `src/main.ts` → not ignored |
| handles missing `.gitignore` gracefully | no error thrown |
| `refresh()` picks up new patterns | pattern added after boot takes effect |

**`file-discovery-service.test.ts`** — real temp directory, no mocking.

| Test | Verifies |
|---|---|
| `getFiles()` returns discovered files | scanned files appear |
| `getFiles(ext)` filters by extension | `.ts` only |
| `getRelativePaths()` returns relative strings | no absolute paths |
| `findFiles()` exact prefix match | `src/main` → `src/main.ts` |
| `findFiles()` fuzzy match | `boot` → matches `bootstrap.ts` |
| `addFile()` adds to cache | appears in `getFiles()` |
| `removeFile()` removes from cache | absent after removal |
| ignored files excluded on boot | `node_modules/` not in results |
| `refresh()` rescans | file added after boot appears after refresh |

**`file-service.test.ts`** — mocks `FileDiscoveryService` (fixed set of discovered files), real temp dir for file reads.

| Test | Verifies |
|---|---|
| `addFile()` single path | appears in `listFiles()` |
| `addFile()` rejects non-discovered file | returns `false` |
| `addFile()` rejects duplicate | returns `false` |
| `addFile()` glob pattern | multiple files added |
| `removeFile()` single path | removed from context |
| `removeFile()` glob pattern | multiple files removed |
| `listFiles()` no filter | all files sorted |
| `listFiles(FileMode.EDITABLE)` | editable only |
| `setFileMode()` | mode reflected in subsequent `listFiles()` |
| `getFileContext()` | correct `FileContext` returned |
| `isFileInContext()` | correct boolean |
| `generateContextPrompt()` | boundaries + fenced code blocks |
| `generateProjectHierarchy()` | returns tree string |

`FileWatcherService` and `AICommentWatcherService` (stub) — not unit tested.

---

## Out of Scope

- `AICommentWatcherService` full implementation — depends on `AskAgent` / `CoderAgent`
- `readFiles` tool full implementation — depends on tools/agent system
- `list_in_context_files_hook` Rich `Columns` layout — Node console prints plain text lists
