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
      status.modified.length  > 0 ||
      status.deleted.length   > 0 ||
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
