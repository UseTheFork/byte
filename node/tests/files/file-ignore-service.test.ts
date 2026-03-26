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

  it('isIgnored() handles relative path input', () => {
    writeFileSync(join(tmpDir, '.gitignore'), 'node_modules\n')
    const svc = new FileIgnoreService(makeApp(tmpDir))
    svc.ensureBooted()
    expect(svc.isIgnored('node_modules/foo.ts')).toBe(true)
    expect(svc.isIgnored('src/main.ts')).toBe(false)
  })
})
