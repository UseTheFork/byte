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
    expect(result).not.toContain('Allowed Commit Scopes')
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
    expect(result).toContain('<CONTEXT>')
    expect(result).toContain('change_type: M')
    expect(result).toContain('file: src/foo.ts')
    expect(result).toContain('<diff>')
    expect(result).toContain('- old')
    expect(result).toContain('</diff>')
    expect(result).toContain('</CONTEXT>')
  })

  it('excludes diff content for deleted files', async () => {
    const entries: DiffEntry[] = [{
      file: 'src/old.ts', changeType: 'D', diff: '',
      message: 'deleted: src/old.ts',
      isModified: false, isNew: false, isDeleted: true, isRenamed: false,
    }]
    const { svc } = makeService({}, entries)
    const result = await svc.buildCommitPrompt()
    expect(result).toContain('change_type: D')
    expect(result).not.toContain('<diff>')
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
