# Git Domain Node/TS Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the git domain from Python to TypeScript — Zod schemas, GitService (repo ops via simple-git), CommitService (conventional commit formatting + prompt building), CommitCommand stub, and GitServiceProvider.

**Architecture:** Schema layer (Zod) → GitService (simple-git, sync boot) → CommitService (pure formatting + prompt assembly, resolves GitService on boot) → GitServiceProvider wires everything into DI. CommitCommand is a registered no-op stub.

**Tech Stack:** TypeScript strict mode, Bun, `bun:test`, `simple-git` (already in package.json), `zod` (already in package.json)

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `node/src/git/schemas.ts` | Create | Zod schemas + inferred types for CommitMessage, CommitGroup, CommitPlan |
| `node/src/git/service/git-service.ts` | Create | GitService: repo ops (getDiff, getChangedFiles, add, remove, reset, commit, stageChanges) |
| `node/src/git/service/commit-service.ts` | Create | CommitService: formatConventionalCommit, buildCommitPrompt, generateCommitGuidelines, processCommitPlan |
| `node/src/git/command/commit-command.ts` | Create | CommitCommand stub (prints "not yet implemented") |
| `node/src/git/tools.ts` | Create | gitGrep stub |
| `node/src/git/service-provider.ts` | Create | GitServiceProvider: registers services + commit command |
| `node/src/git/index.ts` | Create | Barrel: all public exports |
| `node/src/main.ts` | Modify | Add GitServiceProvider to provider list |
| `node/tests/git/schemas.test.ts` | Create | Schema tests |
| `node/tests/git/git-service.test.ts` | Create | GitService tests using real temp git repo |
| `node/tests/git/commit-service.test.ts` | Create | CommitService tests with mocked GitService |

---

### Task 1: Commit schemas

**Files:**
- Create: `node/src/git/schemas.ts`
- Create: `node/tests/git/schemas.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `node/tests/git/schemas.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import {
  CommitMessageSchema,
  CommitGroupSchema,
  CommitPlanSchema,
} from '../../src/git/schemas.ts'

describe('CommitMessageSchema', () => {
  it('parses a minimal commit message with defaults', () => {
    const result = CommitMessageSchema.parse({ type: 'feat', commit_message: 'add thing' })
    expect(result.type).toBe('feat')
    expect(result.commit_message).toBe('add thing')
    expect(result.scope).toBeNull()
    expect(result.breaking_change).toBe(false)
    expect(result.breaking_change_message).toBeNull()
    expect(result.body).toBeNull()
  })

  it('parses a full commit message', () => {
    const result = CommitMessageSchema.parse({
      type: 'feat',
      scope: 'cli',
      commit_message: 'add thing',
      breaking_change: true,
      breaking_change_message: 'removed old API',
      body: 'this changes everything',
    })
    expect(result.scope).toBe('cli')
    expect(result.breaking_change).toBe(true)
    expect(result.breaking_change_message).toBe('removed old API')
    expect(result.body).toBe('this changes everything')
  })
})

describe('CommitGroupSchema', () => {
  it('extends CommitMessage with files', () => {
    const result = CommitGroupSchema.parse({
      type: 'fix',
      commit_message: 'patch bug',
      files: ['src/foo.ts', 'src/bar.ts'],
    })
    expect(result.files).toEqual(['src/foo.ts', 'src/bar.ts'])
    expect(result.scope).toBeNull()
  })

  it('defaults files to empty array', () => {
    const result = CommitGroupSchema.parse({ type: 'fix', commit_message: 'patch' })
    expect(result.files).toEqual([])
  })
})

describe('CommitPlanSchema', () => {
  it('parses a commit plan with multiple groups', () => {
    const result = CommitPlanSchema.parse({
      commits: [
        { type: 'feat', commit_message: 'add foo', files: ['foo.ts'] },
        { type: 'fix', commit_message: 'fix bar', files: ['bar.ts'] },
      ],
    })
    expect(result.commits).toHaveLength(2)
    expect(result.commits[0]?.type).toBe('feat')
    expect(result.commits[1]?.type).toBe('fix')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd node && bun test tests/git/schemas.test.ts
```

Expected: FAIL — cannot find module `../../src/git/schemas.ts`

- [ ] **Step 3: Implement schemas**

Create `node/src/git/schemas.ts`:

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

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd node && bun test tests/git/schemas.test.ts
```

Expected: PASS — 5 tests

- [ ] **Step 5: Commit**

```bash
cd node && git add src/git/schemas.ts tests/git/schemas.test.ts && git commit -m "feat(git): add Zod schemas for CommitMessage, CommitGroup, CommitPlan"
```

---

### Task 2: GitService (TDD)

**Files:**
- Create: `node/src/git/service/git-service.ts`
- Create: `node/tests/git/git-service.test.ts`

**Key notes for implementer:**
- `boot(): void` is synchronous — just calls `simpleGit(rootPath)`. No async needed because `Application.initGitRoot()` already validates the repo at startup.
- `getDiff()` uses `git diff --cached --name-status` to enumerate staged files, then fetches per-file diffs.
- `remove()` uses `git rm --cached` to stage a deletion (file was already deleted from disk).
- `reset()` with no args uses `git raw(['reset', 'HEAD'])` to unstage everything.
- `stageChanges(force)` prompts via `InteractionService` when `force` is false.
- The test mock app returns the right value for any `make()` call — for unknown keys it returns a confirm-always object.

- [ ] **Step 1: Write the failing tests**

Create `node/tests/git/git-service.test.ts`:

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'bun:test'
import { mkdtempSync, writeFileSync, rmSync, unlinkSync } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import { simpleGit } from 'simple-git'
import type { IApplication } from '../../src/support/concerns/bootable.ts'
import { GitService } from '../../src/git/service/git-service.ts'

let tmpDir: string
let service: GitService

async function initRepo(dir: string) {
  const git = simpleGit(dir)
  await git.init()
  await git.addConfig('user.name', 'Test User')
  await git.addConfig('user.email', 'test@example.com')
  writeFileSync(join(dir, 'README.md'), '# Test\n')
  await git.add('README.md')
  await git.commit('initial commit')
  return git
}

function makeApp(rootPath: string): IApplication {
  return {
    make: (key: unknown) => {
      if (key === 'path.root') return rootPath
      if (key === 'console') return { print: () => {}, printError: () => {} }
      // Covers InteractionService and anything else — confirm always true
      return { confirm: async () => true }
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  } as unknown as IApplication
}

beforeEach(async () => {
  tmpDir = mkdtempSync(join(tmpdir(), 'byte-git-test-'))
  await initRepo(tmpDir)
  service = new GitService(makeApp(tmpDir))
  service.ensureBooted()
})

afterEach(() => {
  rmSync(tmpDir, { recursive: true, force: true })
})

describe('GitService.getChangedFiles', () => {
  it('returns modified tracked files', async () => {
    writeFileSync(join(tmpDir, 'README.md'), '# Updated\n')
    const files = await service.getChangedFiles(false)
    expect(files).toContain('README.md')
  })

  it('includes untracked files when includeUntracked is true', async () => {
    writeFileSync(join(tmpDir, 'new-file.ts'), 'export const x = 1\n')
    const files = await service.getChangedFiles(true)
    expect(files).toContain('new-file.ts')
  })

  it('excludes untracked files when includeUntracked is false', async () => {
    writeFileSync(join(tmpDir, 'new-file.ts'), 'export const x = 1\n')
    const files = await service.getChangedFiles(false)
    expect(files).not.toContain('new-file.ts')
  })
})

describe('GitService.add and reset', () => {
  it('stages a file with add() and unstages it with reset(filePath)', async () => {
    writeFileSync(join(tmpDir, 'hello.ts'), 'export const x = 1\n')
    await service.add('hello.ts')

    const git = simpleGit(tmpDir)
    let status = await git.status()
    expect(status.created).toContain('hello.ts')

    await service.reset('hello.ts')
    status = await git.status()
    expect(status.created).not.toContain('hello.ts')
  })

  it('unstages all files when reset() is called with no arguments', async () => {
    writeFileSync(join(tmpDir, 'a.ts'), 'a\n')
    writeFileSync(join(tmpDir, 'b.ts'), 'b\n')
    await service.add('a.ts')
    await service.add('b.ts')

    await service.reset()
    const git = simpleGit(tmpDir)
    const status = await git.status()
    expect(status.created).not.toContain('a.ts')
    expect(status.created).not.toContain('b.ts')
  })
})

describe('GitService.getDiff', () => {
  it('returns empty array when nothing is staged', async () => {
    const diff = await service.getDiff()
    expect(diff).toEqual([])
  })

  it('returns DiffEntry with changeType A for a new staged file', async () => {
    writeFileSync(join(tmpDir, 'new.ts'), 'export const x = 1\n')
    await service.add('new.ts')
    const diff = await service.getDiff()

    const entry = diff.find(e => e.file === 'new.ts')
    expect(entry).toBeDefined()
    expect(entry?.changeType).toBe('A')
    expect(entry?.isNew).toBe(true)
    expect(entry?.isModified).toBe(false)
    expect(entry?.diff).toContain('export const x = 1')
  })

  it('returns DiffEntry with changeType M for a modified staged file', async () => {
    writeFileSync(join(tmpDir, 'README.md'), '# Modified\n')
    await service.add('README.md')
    const diff = await service.getDiff()

    const entry = diff.find(e => e.file === 'README.md')
    expect(entry).toBeDefined()
    expect(entry?.changeType).toBe('M')
    expect(entry?.isModified).toBe(true)
    expect(entry?.diff).toBeTruthy()
  })

  it('returns DiffEntry with changeType D for a deleted staged file', async () => {
    unlinkSync(join(tmpDir, 'README.md'))
    await service.remove('README.md')
    const diff = await service.getDiff()

    const entry = diff.find(e => e.file === 'README.md')
    expect(entry).toBeDefined()
    expect(entry?.changeType).toBe('D')
    expect(entry?.isDeleted).toBe(true)
    expect(entry?.diff).toBe('')
  })
})

describe('GitService.stageChanges', () => {
  it('stages all changes when force is true', async () => {
    writeFileSync(join(tmpDir, 'foo.ts'), 'x\n')
    await service.stageChanges(true)

    const git = simpleGit(tmpDir)
    const status = await git.status()
    expect(status.created).toContain('foo.ts')
  })
})

describe('GitService.commit', () => {
  it('creates a commit with the given message', async () => {
    writeFileSync(join(tmpDir, 'file.ts'), 'x\n')
    await service.add('file.ts')
    await service.commit('feat: add file')

    const git = simpleGit(tmpDir)
    const log = await git.log()
    expect(log.latest?.message).toBe('feat: add file')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd node && bun test tests/git/git-service.test.ts
```

Expected: FAIL — cannot find module `../../src/git/service/git-service.ts`

- [ ] **Step 3: Implement GitService**

Create `node/src/git/service/git-service.ts`:

```typescript
import { simpleGit, type SimpleGit } from 'simple-git'
import { Service } from '../../support/service.ts'
import { InteractionService } from '../../cli/service/interaction-service.ts'

export interface DiffEntry {
  file:       string
  changeType: 'A' | 'D' | 'M' | 'R'
  diff:       string
  message:    string
  isRenamed:  boolean
  isModified: boolean
  isNew:      boolean
  isDeleted:  boolean
  oldFile?:   string
}

export class GitService extends Service {
  static token = Symbol('GitService')
  private git!: SimpleGit

  override boot(): void {
    this.git = simpleGit(this.app.make<string>('path.root'))
  }

  async getChangedFiles(includeUntracked = true): Promise<string[]> {
    const status = await this.git.status()
    const files = new Set<string>()

    for (const f of status.modified) files.add(f)
    for (const f of status.staged)   files.add(f)
    for (const f of status.created)  files.add(f)
    for (const f of status.deleted)  files.add(f)
    for (const r of status.renamed)  files.add(r.to)

    if (includeUntracked) {
      for (const f of status.not_added) files.add(f)
    }

    return [...files]
  }

  async stageChanges(force = false): Promise<void> {
    const status = await this.git.status()
    const hasChanges =
      status.modified.length > 0 ||
      status.deleted.length  > 0 ||
      status.not_added.length > 0

    if (!hasChanges) return

    if (!force) {
      const interaction = this.app.make<InteractionService>(InteractionService)
      const confirmed = await interaction.confirm(
        `Stage ${status.modified.length + status.deleted.length} unstaged and ${status.not_added.length} untracked changes?`
      )
      if (!confirmed) return
    }

    await this.git.add(['-A'])
  }

  async add(filePath: string): Promise<void> {
    await this.git.add([filePath])
  }

  async remove(filePath: string): Promise<void> {
    await this.git.raw(['rm', '--cached', '--', filePath])
  }

  async reset(filePath?: string): Promise<void> {
    if (filePath) {
      await this.git.raw(['reset', 'HEAD', '--', filePath])
    } else {
      await this.git.raw(['reset', 'HEAD'])
    }
  }

  async commit(message: string): Promise<void> {
    await this.git.commit(message)
  }

  async getDiff(): Promise<DiffEntry[]> {
    const nameStatus = await this.git.diff(['--cached', '--name-status'])
    if (!nameStatus.trim()) return []

    const entries: DiffEntry[] = []

    for (const line of nameStatus.split('\n').filter(Boolean)) {
      const parts = line.split('\t')
      const changeTypeRaw = parts[0] ?? ''

      if (changeTypeRaw.startsWith('R')) {
        const oldFile = parts[1] ?? ''
        const file    = parts[2] ?? ''
        const diff    = await this.git.diff(['--cached', '--', file]).catch(() => '')
        entries.push({
          file, oldFile, changeType: 'R', diff,
          message: `renamed: ${oldFile} -> ${file}`,
          isRenamed: true, isModified: false, isNew: false, isDeleted: false,
        })
        continue
      }

      const file       = parts[1] ?? ''
      const changeType = changeTypeRaw as 'A' | 'D' | 'M'
      let diff    = ''
      let message = ''

      if (changeType === 'A') {
        message = `new: ${file}`
        try {
          const content = await this.git.show([`:${file}`])
          diff = content.includes('\0') ? '' : content
        } catch { diff = '' }
      } else if (changeType === 'M') {
        message = `modified: ${file}`
        diff = await this.git.diff(['--cached', '--', file]).catch(() => '')
      } else {
        message = `deleted: ${file}`
        diff = ''
      }

      entries.push({
        file, changeType, diff, message,
        isNew:      changeType === 'A',
        isModified: changeType === 'M',
        isDeleted:  changeType === 'D',
        isRenamed:  false,
      })
    }

    return entries
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd node && bun test tests/git/git-service.test.ts
```

Expected: PASS — 9 tests

- [ ] **Step 5: Run full suite to confirm no regressions**

```bash
cd node && bun test
```

Expected: all existing tests still pass

- [ ] **Step 6: Commit**

```bash
cd node && git add src/git/service/git-service.ts tests/git/git-service.test.ts && git commit -m "feat(git): implement GitService with simple-git"
```

---

### Task 3: CommitService (TDD)

**Files:**
- Create: `node/src/git/service/commit-service.ts`
- Create: `node/tests/git/commit-service.test.ts`

**Key notes:**
- `formatConventionalCommit` is synchronous and pure — no I/O, no prompts.
- Breaking change `!` and footer are applied automatically when `breaking_change: true` and `enable_breaking_changes: true`. No user confirmation needed (that's a CommitCommand concern for later).
- `processCommitPlan` always calls `gitService.add()` for each file — `git add` handles deletions automatically (if the file is gone from disk, git stages the deletion).
- `CommitService` imports `GitService` as a value (needed for `this.app.make(GitService)` which uses the class as DI key). All other imports from config/schemas are `import type`.

- [ ] **Step 1: Write the failing tests**

Create `node/tests/git/commit-service.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import type { IApplication } from '../../src/support/concerns/bootable.ts'
import { CommitService } from '../../src/git/service/commit-service.ts'
import { GitService } from '../../src/git/service/git-service.ts'
import type { DiffEntry } from '../../src/git/service/git-service.ts'
import type { ByteConfig } from '../../src/config/schemas.ts'

type GitConfig = ByteConfig['git']

function makeApp(gitConfig: Partial<GitConfig> = {}, diffEntries: DiffEntry[] = []) {
  const config: GitConfig = {
    enable_scopes:           true,
    enable_breaking_changes: true,
    enable_body:             true,
    scopes:                  ['api', 'cli', 'config'],
    description_guidelines:  [],
    max_description_length:  72,
    ...gitConfig,
  }

  const tracking = {
    addedFiles:  [] as string[],
    commits:     [] as string[],
    resetCalled: false,
  }

  const mockGitService = {
    getDiff:  async (): Promise<DiffEntry[]> => diffEntries,
    reset:    async () => { tracking.resetCalled = true },
    add:      async (f: string) => { tracking.addedFiles.push(f) },
    remove:   async (_f: string) => {},
    commit:   async (msg: string) => { tracking.commits.push(msg) },
  }

  const mockApp: IApplication = {
    make: (key: unknown) => {
      if (key === GitService) return mockGitService
      if (key === 'config') return { git: config } as ByteConfig
      return undefined
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  } as unknown as IApplication

  return { mockApp, tracking }
}

function makeService(gitConfig: Partial<GitConfig> = {}, diffEntries: DiffEntry[] = []) {
  const { mockApp, tracking } = makeApp(gitConfig, diffEntries)
  const svc = new CommitService(mockApp)
  svc.ensureBooted()
  return { svc, tracking }
}

describe('CommitService.formatConventionalCommit', () => {
  it('formats a basic commit', () => {
    const { svc } = makeService()
    const result = svc.formatConventionalCommit({
      type: 'feat', commit_message: 'Add thing',
      scope: null, breaking_change: false, breaking_change_message: null, body: null,
    })
    expect(result).toBe('feat: add thing')
  })

  it('lowercases first character and strips trailing period', () => {
    const { svc } = makeService()
    const result = svc.formatConventionalCommit({
      type: 'fix', commit_message: 'Fix crash.',
      scope: null, breaking_change: false, breaking_change_message: null, body: null,
    })
    expect(result).toBe('fix: fix crash')
  })

  it('formats with scope when enable_scopes is true', () => {
    const { svc } = makeService({ enable_scopes: true })
    const result = svc.formatConventionalCommit({
      type: 'feat', commit_message: 'add thing', scope: 'cli',
      breaking_change: false, breaking_change_message: null, body: null,
    })
    expect(result).toBe('feat(cli): add thing')
  })

  it('strips scope when enable_scopes is false', () => {
    const { svc } = makeService({ enable_scopes: false })
    const result = svc.formatConventionalCommit({
      type: 'feat', commit_message: 'add thing', scope: 'cli',
      breaking_change: false, breaking_change_message: null, body: null,
    })
    expect(result).toBe('feat: add thing')
  })

  it('adds breaking change marker and footer when enable_breaking_changes is true', () => {
    const { svc } = makeService({ enable_breaking_changes: true })
    const result = svc.formatConventionalCommit({
      type: 'feat', commit_message: 'remove old api', scope: null,
      breaking_change: true, breaking_change_message: 'removed /v1 endpoints', body: null,
    })
    expect(result).toContain('feat!: remove old api')
    expect(result).toContain('BREAKING CHANGE: removed /v1 endpoints')
  })

  it('omits breaking change when enable_breaking_changes is false', () => {
    const { svc } = makeService({ enable_breaking_changes: false })
    const result = svc.formatConventionalCommit({
      type: 'feat', commit_message: 'remove old api', scope: null,
      breaking_change: true, breaking_change_message: 'removed /v1', body: null,
    })
    expect(result).toBe('feat: remove old api')
    expect(result).not.toContain('!')
    expect(result).not.toContain('BREAKING CHANGE')
  })

  it('includes body when enable_body is true', () => {
    const { svc } = makeService({ enable_body: true })
    const result = svc.formatConventionalCommit({
      type: 'fix', commit_message: 'fix crash', scope: null,
      breaking_change: false, breaking_change_message: null,
      body: 'Prevents null pointer on startup',
    })
    expect(result).toContain('Prevents null pointer on startup')
  })

  it('omits body when enable_body is false', () => {
    const { svc } = makeService({ enable_body: false })
    const result = svc.formatConventionalCommit({
      type: 'fix', commit_message: 'fix crash', scope: null,
      breaking_change: false, breaking_change_message: null,
      body: 'Prevents null pointer on startup',
    })
    expect(result).not.toContain('Prevents null pointer on startup')
  })
})

describe('CommitService.generateCommitGuidelines', () => {
  it('contains all 10 commit types', () => {
    const { svc } = makeService()
    const result = svc.generateCommitGuidelines()
    for (const t of ['feat', 'fix', 'refactor', 'perf', 'style', 'test', 'build', 'ops', 'docs', 'chore']) {
      expect(result).toContain(t)
    }
  })

  it('includes max_description_length in guidelines', () => {
    const { svc } = makeService({ max_description_length: 72 })
    const result = svc.generateCommitGuidelines()
    expect(result).toContain('72')
  })

  it('includes scope list when enable_scopes is true', () => {
    const { svc } = makeService({ enable_scopes: true, scopes: ['api', 'cli'] })
    const result = svc.generateCommitGuidelines()
    expect(result).toContain('- api')
    expect(result).toContain('- cli')
  })

  it('includes DO NOT include scope rule when enable_scopes is false', () => {
    const { svc } = makeService({ enable_scopes: false })
    const result = svc.generateCommitGuidelines()
    expect(result).toContain('DO NOT include `scope`')
  })
})

describe('CommitService.buildCommitPrompt', () => {
  it('wraps each diff entry in CONTEXT boundaries', async () => {
    const entries: DiffEntry[] = [{
      file: 'src/foo.ts', changeType: 'M', diff: '- old\n+ new',
      message: 'modified: src/foo.ts',
      isModified: true, isNew: false, isDeleted: false, isRenamed: false,
    }]
    const { svc } = makeService({}, entries)
    const result = await svc.buildCommitPrompt()
    expect(result).toContain('<context')
    expect(result).toContain('change_type="M"')
    expect(result).toContain('file="src/foo.ts"')
    expect(result).toContain('- old')
    expect(result).toContain('</context>')
  })

  it('excludes diff content for deleted files', async () => {
    const entries: DiffEntry[] = [{
      file: 'src/old.ts', changeType: 'D', diff: '',
      message: 'deleted: src/old.ts',
      isModified: false, isNew: false, isDeleted: true, isRenamed: false,
    }]
    const { svc } = makeService({}, entries)
    const result = await svc.buildCommitPrompt()
    expect(result).toContain('change_type="D"')
    expect(result).not.toContain('+ ')
  })
})

describe('CommitService.processCommitPlan', () => {
  it('resets, then stages and commits each group in order', async () => {
    const { svc, tracking } = makeService()
    await svc.processCommitPlan({
      commits: [
        { type: 'feat', commit_message: 'add foo', scope: null, breaking_change: false, breaking_change_message: null, body: null, files: ['src/foo.ts'] },
        { type: 'fix',  commit_message: 'fix bar', scope: null, breaking_change: false, breaking_change_message: null, body: null, files: ['src/bar.ts'] },
      ],
    })

    expect(tracking.resetCalled).toBe(true)
    expect(tracking.addedFiles).toContain('src/foo.ts')
    expect(tracking.addedFiles).toContain('src/bar.ts')
    expect(tracking.commits).toHaveLength(2)
    expect(tracking.commits[0]).toBe('feat: add foo')
    expect(tracking.commits[1]).toBe('fix: fix bar')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd node && bun test tests/git/commit-service.test.ts
```

Expected: FAIL — cannot find module `../../src/git/service/commit-service.ts`

- [ ] **Step 3: Implement CommitService**

Create `node/src/git/service/commit-service.ts`:

```typescript
import { Service } from '../../support/service.ts'
import { Boundary, BoundaryType } from '../../support/boundary.ts'
import type { ByteConfig } from '../../config/schemas.ts'
import type { CommitMessage, CommitGroup, CommitPlan } from '../schemas.ts'
import { GitService } from './git-service.ts'

const COMMIT_TYPES: Record<string, string> = {
  feat:     'Commits that add or remove a new feature to the API or UI',
  fix:      'Commits that fix an API or UI bug of a preceded feat commit',
  refactor: 'Commits that rewrite/restructure code without changing API or UI behaviour',
  perf:     'Commits that improve performance (special refactor commits)',
  style:    'Commits that do not affect meaning (white-space, formatting, missing semi-colons, etc)',
  test:     'Commits that add missing tests or correct existing tests',
  build:    'Commits that affect build components (build tool, CI pipeline, dependencies, project version, etc)',
  ops:      'Commits that affect operational components (infrastructure, deployment, backup, recovery, etc)',
  docs:     'Commits that affect documentation only',
  chore:    'Commits that represent tasks (initial commit, modifying .gitignore, etc)',
}

export class CommitService extends Service {
  static token = Symbol('CommitService')
  private gitService!: GitService
  private config!: ByteConfig['git']

  override boot(): void {
    this.gitService = this.app.make<GitService>(GitService)
    this.config = this.app.make<ByteConfig>('config').git
  }

  formatConventionalCommit(msg: CommitMessage | CommitGroup): string {
    const headerParts: string[] = [msg.type]

    if (this.config.enable_scopes && msg.scope) {
      headerParts.push(`(${msg.scope})`)
    }

    let description = msg.commit_message
    description = description.charAt(0).toLowerCase() + description.slice(1)
    description = description.replace(/\.$/, '')

    const messageParts: string[] = []
    let breakingChangeFooter: string | null = null

    if (this.config.enable_breaking_changes && msg.breaking_change) {
      headerParts.push('!')
      if (msg.breaking_change_message) {
        breakingChangeFooter = `BREAKING CHANGE: ${msg.breaking_change_message}`
      }
    }

    messageParts.push(headerParts.join('') + `: ${description}`)

    if (this.config.enable_body && msg.body) {
      messageParts.push('', msg.body)
    }

    if (breakingChangeFooter) {
      messageParts.push('', breakingChangeFooter)
    }

    return messageParts.join('\n')
  }

  async buildCommitPrompt(): Promise<string> {
    const staged = await this.gitService.getDiff()
    const diffParts: string[] = []
    const fileParts: string[] = [Boundary.open(BoundaryType.CONTEXT, { type: 'Files' })]

    for (const entry of staged) {
      diffParts.push(Boundary.open(BoundaryType.CONTEXT, {
        type: 'Diff',
        change_type: entry.changeType,
        file: entry.file,
      }))
      fileParts.push(entry.message)
      if (entry.changeType !== 'D' && entry.diff) {
        diffParts.push(entry.diff)
      }
      diffParts.push(Boundary.close(BoundaryType.CONTEXT))
    }

    fileParts.push(Boundary.close(BoundaryType.CONTEXT))
    return [...diffParts, ...fileParts].join('\n')
  }

  generateCommitGuidelines(): string {
    const parts: string[] = []

    parts.push(Boundary.open(BoundaryType.RULES, { type: 'Allowed Commit Types' }))
    parts.push(Object.entries(COMMIT_TYPES).map(([t, d]) => `- **${t}**: ${d}`).join('\n'))
    parts.push(Boundary.close(BoundaryType.RULES))

    parts.push(Boundary.open(BoundaryType.RULES, { type: 'Commit Description Guidelines' }))
    const descGuidelines = [
      "- Use imperative mood (e.g., 'add feature' not 'added feature')",
      '- Start with lowercase letter',
      '- Do not end with a period',
      `- Keep under ${this.config.max_description_length} characters`,
      '- Be concise and descriptive',
      '- Focus on what the change does, not how it does it',
      ...this.config.description_guidelines.map(g => `- ${g}`),
    ]
    parts.push(descGuidelines.join('\n'))
    parts.push(Boundary.close(BoundaryType.RULES))

    parts.push(Boundary.open(BoundaryType.RULES, { type: 'Allowed Commit Scopes' }))
    if (this.config.enable_scopes && this.config.scopes.length > 0) {
      parts.push(this.config.scopes.map(s => `- ${s}`).join('\n'))
    }
    parts.push(Boundary.close(BoundaryType.RULES))

    parts.push(Boundary.open(BoundaryType.RULES, { type: 'Field Inclusion Rules' }))
    const fieldRules: string[] = []
    if (!this.config.enable_scopes)           fieldRules.push('- DO NOT include `scope` in the commit message')
    if (!this.config.enable_body)             fieldRules.push('- DO NOT include `body` in the commit message')
    if (!this.config.enable_breaking_changes) fieldRules.push('- DO NOT include `breaking_change` or `breaking_change_message` in the commit message')
    if (fieldRules.length === 0)              fieldRules.push('- All optional fields are enabled and may be included when appropriate')
    parts.push(fieldRules.join('\n'))
    parts.push(Boundary.close(BoundaryType.RULES))

    return parts.join('\n')
  }

  async processCommitPlan(plan: CommitPlan): Promise<void> {
    await this.gitService.reset()
    for (const group of plan.commits) {
      for (const filePath of group.files) {
        await this.gitService.add(filePath)
      }
      await this.gitService.commit(this.formatConventionalCommit(group))
    }
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd node && bun test tests/git/commit-service.test.ts
```

Expected: PASS — 14 tests

- [ ] **Step 5: Run full suite**

```bash
cd node && bun test
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
cd node && git add src/git/service/commit-service.ts tests/git/commit-service.test.ts && git commit -m "feat(git): implement CommitService with conventional commit formatting"
```

---

### Task 4: Wiring — ServiceProvider, CommitCommand, tools, barrel, main.ts

**Files:**
- Create: `node/src/git/command/commit-command.ts`
- Create: `node/src/git/tools.ts`
- Create: `node/src/git/service-provider.ts`
- Create: `node/src/git/index.ts`
- Modify: `node/src/main.ts`

No TDD for this task — all files are stubs or wiring; correctness is verified by booting the app and running the full test suite.

- [ ] **Step 1: Create CommitCommand stub**

Create `node/src/git/command/commit-command.ts`:

```typescript
import { Command } from '../../cli/service/command-registry.ts'

export class CommitCommand extends Command {
  get name() { return 'commit' }
  get description() { return 'Create a conventional commit (coming soon)' }

  async execute(_args: string): Promise<void> {
    this.app.make<{ print(msg: string): void }>('console').print('not yet implemented')
  }
}
```

- [ ] **Step 2: Create tools stub**

Create `node/src/git/tools.ts`:

```typescript
export async function gitGrep(_pattern: string, _filePattern = ''): Promise<string> {
  return ''
}
```

- [ ] **Step 3: Create GitServiceProvider**

Create `node/src/git/service-provider.ts`:

```typescript
import { ServiceProvider } from '../support/service-provider.ts'
import { CommandRegistry } from '../cli/service/command-registry.ts'
import { GitService } from './service/git-service.ts'
import { CommitService } from './service/commit-service.ts'
import { CommitCommand } from './command/commit-command.ts'

export class GitServiceProvider extends ServiceProvider {
  override register(): void {
    this.app.singleton(GitService as never, () => {
      const svc = new GitService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(CommitService as never, () => {
      const svc = new CommitService(this.app)
      svc.ensureBooted()
      return svc
    })
  }

  override async boot(): Promise<void> {
    const registry = this.app.make<CommandRegistry>(CommandRegistry as never)
    registry.register(new CommitCommand(this.app))
  }
}
```

- [ ] **Step 4: Create barrel**

Create `node/src/git/index.ts`:

```typescript
export { CommitMessageSchema, CommitGroupSchema, CommitPlanSchema } from './schemas.ts'
export type { CommitMessage, CommitGroup, CommitPlan } from './schemas.ts'
export { GitService } from './service/git-service.ts'
export type { DiffEntry } from './service/git-service.ts'
export { CommitService } from './service/commit-service.ts'
export { GitServiceProvider } from './service-provider.ts'
```

- [ ] **Step 5: Add GitServiceProvider to main.ts**

Read `node/src/main.ts` first. It currently lists `FoundationServiceProvider` and `CLIServiceProvider`. Add `GitServiceProvider` as the third entry:

```typescript
import React from 'react'
import { render } from 'ink'
import { Application } from './foundation/application.ts'
import { FoundationServiceProvider } from './foundation/service-provider.ts'
import { CLIServiceProvider } from './cli/service-provider.ts'
import { GitServiceProvider } from './git/service-provider.ts'
import { Console } from './cli/service/console.ts'
import { PromptService } from './cli/service/prompt-service.ts'
import { App } from './cli/components/app.tsx'

const app = Application.configure(process.cwd(), [
  FoundationServiceProvider as never,
  CLIServiceProvider as never,
  GitServiceProvider as never,
]).create()

await app.boot()

const consoleService = app.make<Console>('console')
const promptService = app.make<PromptService>(PromptService as never)
const cachePath = app.make<string>('path.cache')

render(React.createElement(App, { consoleService, promptService, cachePath }))
```

- [ ] **Step 6: Run full test suite**

```bash
cd node && bun test
```

Expected: all tests pass (150+ tests)

- [ ] **Step 7: Commit**

```bash
cd node && git add src/git/command/commit-command.ts src/git/tools.ts src/git/service-provider.ts src/git/index.ts src/main.ts && git commit -m "feat(git): add GitServiceProvider, CommitCommand stub, and wire into main"
```
