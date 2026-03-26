export const BoundaryType = {
  ROLE: 'role',
  TASK: 'task',
  USER_INPUT: 'user_input',
  CORE_MANDATES: 'core_mandates',
  GOAL: 'goal',
  RESPONSE_FORMAT: 'response_format',
  RULES: 'rules',
  ERROR: 'error',
  NAME: 'name',
  DESCRIPTION: 'description',
  LOCATION: 'location',
  AVAILABLE_CONVENTIONS: 'available_conventions',
  CONVENTION: 'convention',
  REFERENCE: 'reference',
  SESSION_CONTEXT: 'session_context',
  SHELL_COMMAND: 'shell_command',
  FILE: 'file',
  EDIT_BLOCK: 'operation_block',
  SEARCH: 'search',
  REPLACE: 'replace',
  EXAMPLE: 'example',
  REINFORCEMENT: 'reinforcement',
  PROJECT_HIERARCHY: 'project_hierarchy',
  CONSTRAINTS: 'constraints',
  PLAN: 'agent_plan',
  GUIDELINES: 'guidelines',
  OPERATING_CONSTRAINTS: 'operating_constraints',
  OPERATING_PRINCIPLES: 'operating_principles',
  CRITICAL_REQUIREMENTS: 'response_requirements',
  RECOVERY_STEPS: 'recovery_steps',
  RESPONSE_TEMPLATE: 'response_template',
  CONTEXT: 'context',
  STDOUT: 'stdout',
  STDERR: 'stderr',
  SYSTEM_CONTEXT: 'system_context',
  NOTE: 'note',
  HEADING: 'heading',
  CONVERSATION_HISTORY: 'conversation_history',
  AGENT_MESSAGE: 'agent_message',
  USER_MESSAGE: 'user_message',
} as const

export type BoundaryType = (typeof BoundaryType)[keyof typeof BoundaryType]

type FormatStyle = 'xml' | 'markdown'

export class Boundary {
  static open(type: BoundaryType, meta?: Record<string, string>, format: FormatStyle = 'xml'): string {
    if (format !== 'xml' && format !== 'markdown') throw new Error(`format must be 'xml' or 'markdown', got '${format}'`)
    if (format === 'xml') {
      const metaStr = meta ? ' ' + Object.entries(meta).map(([k, v]) => `${k}="${v}"`).join(' ') : ''
      return `<${type}${metaStr}>`
    }
    const titleStr = meta?.['title'] ? `: ${meta['title']}` : ''
    const label = type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    return `## ${label}${titleStr}`
  }

  static close(type: BoundaryType, format: FormatStyle = 'xml'): string {
    if (format !== 'xml' && format !== 'markdown') throw new Error(`format must be 'xml' or 'markdown', got '${format}'`)
    return format === 'xml' ? `</${type}>` : ''
  }

  static notice(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- NOTICE: ${content} -->` : content
  }

  static critical(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- **CRITICAL: ${content}** -->` : `**${content}**`
  }

  static important(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- **IMPORTANT: ${content}** -->` : `**${content}**`
  }

  static warning(content: string, format: FormatStyle = 'xml'): string {
    return format === 'xml' ? `<!-- **WARNING:${content}** -->` : `**${content}**`
  }

  static comment(content: string): string {
    return `<!-- \n${content}\n -->`
  }
}
