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
