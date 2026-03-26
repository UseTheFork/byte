# Design: Git Domain — Python to Node/TS Migration

**Date:** 2026-03-26
**Branch:** dev-v3-node
**Scope:** `git` domain — schemas, `GitService`, `CommitService`, `GitServiceProvider`, `CommitCommand` stub, `tools.ts` stub. `CommitValidator` is out of scope (depends on agent validation framework). Python source is preserved and serves as the reference implementation.

---

## Overview

Port the git layer of the byte CLI from Python (GitPython + Pydantic) to TypeScript (simple-git + Zod), running under Bun. After this migration, `GitService` manages repository operations and `CommitService` handles conventional commit formatting and prompt building — both fully typed and DI-wired. The `/commit` command is registered as a stub ("not yet implemented") pending agent domain migration.

---

## Tooling Additions

None. `simple-git` is already present in `package.json`.

---

## Repository Layout

```
node/src/git/
  index.ts                        ← barrel
  schemas.ts                      ← CommitMessage, CommitGroup, CommitPlan (Zod)
  service-provider.ts             ← GitServiceProvider
  tools.ts                        ← gitGrep stub
  service/
    git-service.ts                ← GitService: repo ops
    commit-service.ts             ← CommitService: formatting + prompt building
  command/
    commit-command.ts             ← CommitCommand: stub

node/tests/git/
  git-service.test.ts
  commit-service.test.ts
```

**Modified files:**
- `node/src/foundation/application-builder.ts` — add `GitServiceProvider` to default providers (or leave for user to wire; see ServiceProvider section)

---

## Architecture

### Schemas (`schemas.ts`)

```typescript
import { z } from 'zod'

export const CommitMessageSchema = z.object({
  type:                    z.string(),
  scope:                   z.string().nullable().default(null),
  commit_message:          z.string(),
  breaking_change:         z.boolean().default(false),
  breaking_change_message: z.string().nullable().default(null),
  body:                    z.string().nullable().default(null),
})

export const CommitGroupSchema = CommitMessageSchema.extend({
  files: z.array(z.string()).default([]),
})

export const CommitPlanSchema = z.object({
  commits: z.array(CommitGroupSchema),
})

export type CommitMessage = z.infer<typeof CommitMessageSchema>
export type CommitGroup   = z.infer<typeof CommitGroupSchema>
export type CommitPlan    = z.infer<typeof CommitPlanSchema>
```

`CommitGroup` extends `CommitMessage` via `.extend()`, matching the Python inheritance pattern.

### `DiffEntry` (internal to `git-service.ts`)

```typescript
export interface DiffEntry {
  file:       string
  changeType: 'A' | 'D' | 'M' | 'R'
  diff:       string
  message:    string
  isRenamed:  boolean
  isModified: boolean
  isNew:      boolean
  isDeleted:  boolean
  oldFile?:   string   // renames only
}
```

---

### `GitService` (`service/git-service.ts`)

Extends `Service`. Initialised in `boot()` using `simple-git` pointed at `app.rootPath()`.

```typescript
import { simpleGit, type SimpleGit } from 'simple-git'

class GitService extends Service {
  static token = Symbol('GitService')
  private git!: SimpleGit

  async boot(): Promise<void> {
    this.git = simpleGit(this.app.rootPath())
    const isRepo = await this.git.checkIsRepo()
    if (!isRepo) throw new Error(`No Git repository found at ${this.app.rootPath()}`)
  }

  async getChangedFiles(includeUntracked = true): Promise<string[]>
  async stageChanges(force = false): Promise<void>
  async commit(message: string): Promise<void>
  async add(filePath: string): Promise<void>
  async remove(filePath: string): Promise<void>
  async reset(filePath?: string): Promise<void>
  async getDiff(): Promise<DiffEntry[]>
}
```

**`getDiff()` logic:**
1. Run `git diff --cached --name-status` to enumerate staged files and change types.
2. For each entry:
   - `A` (new): run `git show :file` to get full staged content; if content contains null bytes → binary, set `diff: ''`.
   - `M` (modified): run `git diff --cached -- file` to get the unified diff.
   - `D` (deleted): `diff: ''`.
   - `R` (renamed): extract old and new paths; run `git diff --cached` for the rename diff.
3. Return `DiffEntry[]` with status flags derived from `changeType`.

**`getChangedFiles()`** — returns deduplicated list of modified, staged, and (optionally) untracked file paths using `git.status()`.

**`stageChanges(force)`** — if `force` is true, runs `git add -A`. Otherwise prompts the user via `InteractionService.confirm()` before staging unstaged/untracked files.

**`commit(message)`** — calls `git.commit(message)`. On failure, surfaces error via `Console` service and throws.

**User interaction** — `InteractionService` resolved via `this.app.make(InteractionService)` in `boot()`.

---

### `CommitService` (`service/commit-service.ts`)

Extends `Service`. Resolves `GitService` and `GitConfig` on `boot()`.

```typescript
class CommitService extends Service {
  static token = Symbol('CommitService')
  private gitService!: GitService
  private config!: GitConfig

  async boot(): Promise<void> {
    this.gitService = this.app.make<GitService>(GitService)
    this.config = this.app.make<ByteConfig>('config').git
  }

  formatConventionalCommit(msg: CommitMessage | CommitGroup): string
  async buildCommitPrompt(): Promise<string>
  generateCommitGuidelines(): string
  async processCommitPlan(plan: CommitPlan): Promise<void>
}
```

**Commit types** (10): `feat, fix, refactor, perf, style, test, build, ops, docs, chore`

**`formatConventionalCommit(msg)`** — pure, no I/O:
- Header: `type[scope][!]: description`
  - Scope omitted if `config.enable_scopes === false` or `msg.scope === null`
  - `!` appended to type+scope if `config.enable_breaking_changes && msg.breaking_change`
  - Description: lowercase first char, strip trailing period
- Body: appended if `config.enable_body && msg.body !== null`
- Footer: `BREAKING CHANGE: <message>` appended if `enable_breaking_changes && breaking_change && breaking_change_message !== null`

**`buildCommitPrompt()`** — calls `getDiff()`, wraps each entry in `<CONTEXT>` boundaries:
```
<CONTEXT>
change_type: M
file: src/foo.ts
<diff>
... unified diff content ...
</diff>
</CONTEXT>
```
Returns full prompt string for agent consumption.

**`generateCommitGuidelines()`** — returns rules string wrapped in `<RULES>` boundaries:
- Commit types list
- `max_description_length` rule
- `description_guidelines` from config (appended verbatim)
- Allowed scopes (only if `enable_scopes`)
- Body / breaking change field rules

**`processCommitPlan(plan)`** — unstages everything (`reset()`), then for each `CommitGroup` in order: `add()` each file, `commit(formatConventionalCommit(group))`.

---

### `CommitCommand` (`command/commit-command.ts`)

Stub — prints "not yet implemented":

```typescript
export class CommitCommand extends Command {
  get name() { return 'commit' }
  get description() { return 'Create a conventional commit (coming soon)' }
  async execute(_args: string): Promise<void> {
    this.app.make<Console>('console').print('not yet implemented')
  }
}
```

---

### `tools.ts`

Stub — shape exported, body is a no-op:

```typescript
export async function gitGrep(_pattern: string, _filePattern = ''): Promise<string> {
  return ''
}
```

---

### `GitServiceProvider` (`service-provider.ts`)

```typescript
class GitServiceProvider extends ServiceProvider {
  services() {
    return [GitService, CommitService]
  }

  async boot(): Promise<void> {
    const registry = this.app.make(CommandRegistry)
    registry.register(new CommitCommand(this.app))
  }
}
```

`GitServiceProvider` is added to the provider list in `main.ts` (not wired into `ApplicationBuilder` defaults — keeping the builder focused on foundation/CLI only).

---

### Barrel (`index.ts`)

```typescript
export { CommitMessageSchema, CommitGroupSchema, CommitPlanSchema } from './schemas.ts'
export type { CommitMessage, CommitGroup, CommitPlan } from './schemas.ts'
export { GitService } from './service/git-service.ts'
export type { DiffEntry } from './service/git-service.ts'
export { CommitService } from './service/commit-service.ts'
export { GitServiceProvider } from './service-provider.ts'
```

---

### Testing

**`git-service.test.ts`** — uses a real temp git repo created in `beforeEach` via `fs.mkdtempSync` + `simpleGit().init()` + initial commit. No mocking of `simple-git`.

| Test | What it verifies |
|---|---|
| `getChangedFiles` — modified | Returns modified tracked file |
| `getChangedFiles` — untracked | Returns untracked file when `includeUntracked: true` |
| `getChangedFiles` — excludes untracked | Untracked omitted when `includeUntracked: false` |
| `getDiff` — new file (A) | Returns `isNew: true`, full content in `diff` |
| `getDiff` — modified file (M) | Returns `isModified: true`, unified diff in `diff` |
| `getDiff` — deleted file (D) | Returns `isDeleted: true`, `diff: ''` |
| `getDiff` — renamed file (R) | Returns `isRenamed: true`, both `file` and `oldFile` populated |
| `add` / `remove` / `reset` | Staged state changes as expected |

**`commit-service.test.ts`** — mocks `GitService.getDiff`. Mock app provides `GitService` and `ByteConfig`.

| Test | What it verifies |
|---|---|
| `formatConventionalCommit` — basic | `feat: add thing` |
| `formatConventionalCommit` — with scope | `feat(cli): add thing` (only when `enable_scopes: true`) |
| `formatConventionalCommit` — scope ignored when disabled | Scope stripped when `enable_scopes: false` |
| `formatConventionalCommit` — breaking change | Header has `!`, footer has `BREAKING CHANGE:` |
| `formatConventionalCommit` — body | Body appended when `enable_body: true` |
| `formatConventionalCommit` — body suppressed | Body omitted when `enable_body: false` |
| `generateCommitGuidelines` | Contains commit types, max_description_length rule |
| `buildCommitPrompt` | Each diff entry wrapped in `<CONTEXT>` boundaries |
| `processCommitPlan` | `reset` called, then `add` + `commit` per group in order |

---

## Out of Scope

- `CommitValidator` — depends on agent validation framework
- `CommitCommand` full implementation — depends on `CommitAgent` / `CommitPlanAgent`
- `gitGrep` full implementation — depends on LangChain tools system
- Agent integration in `CommitService` (no agent calls)
- Lint runner integration in `CommitCommand`
