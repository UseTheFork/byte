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

  it('findFiles() returns tier-1 prefix matches before tier-2 filename matches', () => {
    // 'src/utils' is in 'src/utils.ts' (tier 1, relative path starts with 'src/utils')
    // Also create a file where 'utils' appears in path but not as prefix
    const deepFile = join(tmpDir, 'lib/utils-helper.ts')
    mkdirSync(join(tmpDir, 'lib'), { recursive: true })
    writeFileSync(deepFile, '')
    service.refresh()

    const results = service.findFiles('src/utils')
    // 'src/utils.ts' matches tier 1 (relative path starts with 'src/utils')
    // 'lib/utils-helper.ts' matches tier 2 or tier 3 (filename or path contains 'utils')
    expect(results[0]).toBe(join(tmpDir, 'src/utils.ts'))
  })
})
