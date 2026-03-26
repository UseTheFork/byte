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
    hasFile: (filePath: string) => discoveredFiles.includes(filePath),
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

  it('generateContextPromptWithLineNumbers() prefixes lines with line numbers', async () => {
    await service.addFile(mainTs, FileMode.READ_ONLY)
    const [readOnly] = await service.generateContextPromptWithLineNumbers()
    expect(readOnly).toHaveLength(1)
    expect(readOnly[0]).toContain('<file')
    expect(readOnly[0]).toContain('   1 | const x = 1')
    expect(readOnly[0]).toContain('</file>')
  })

  it('listInContextFilesHook() appends file lists to info_panel', async () => {
    await service.addFile(mainTs, FileMode.READ_ONLY)
    await service.addFile(utilsTs, FileMode.EDITABLE)
    const { Payload } = await import('../../src/support/concerns/eventable.ts')
    const payload = new Payload('test', { info_panel: 'existing\n' })
    const result = await service.listInContextFilesHook(payload)
    const panel = result.get('info_panel') as string
    expect(panel).toContain('Read-only files:')
    expect(panel).toContain('src/main.ts')
    expect(panel).toContain('Editable files:')
    expect(panel).toContain('src/utils.ts')
  })
})
