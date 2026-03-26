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

    for (const entry of staged) {
      const lines: string[] = []
      lines.push('<CONTEXT>')
      lines.push(`change_type: ${entry.changeType}`)
      lines.push(`file: ${entry.file}`)
      if ((entry.changeType === 'M' || entry.changeType === 'A' || entry.changeType === 'R') && entry.diff) {
        lines.push('<diff>')
        lines.push(entry.diff)
        lines.push('</diff>')
      }
      lines.push('</CONTEXT>')
      diffParts.push(lines.join('\n'))
    }

    return diffParts.join('\n')
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
      ...this.config.description_guidelines,
    ]
    parts.push(descGuidelines.join('\n'))
    parts.push(Boundary.close(BoundaryType.RULES))

    if (this.config.enable_scopes && this.config.scopes.length > 0) {
      parts.push(Boundary.open(BoundaryType.RULES, { type: 'Allowed Commit Scopes' }))
      parts.push(this.config.scopes.map(s => `- ${s}`).join('\n'))
      parts.push(Boundary.close(BoundaryType.RULES))
    }

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
    if (plan.commits.length === 0) return
    await this.gitService.reset()
    for (const group of plan.commits) {
      if (group.files.length === 0) continue
      for (const filePath of group.files) {
        await this.gitService.add(filePath)
      }
      await this.gitService.commit(this.formatConventionalCommit(group))
    }
  }
}
