import { Command } from '../service/command-registry.ts'
import type { CommandRegistry } from '../service/command-registry.ts'

export class HelpCommand extends Command {
  get name() { return 'help' }
  get description() { return 'Show available commands' }

  async execute(_args: string): Promise<void> {
    const registry = this.app.make<CommandRegistry>('command-registry')
    const console = this.app.make<{ print(t: string, style?: string): void }>('console')
    const completions = registry.getCompletions('')
    console.print('Available commands:', 'muted')
    for (const [name, description] of completions) {
      console.print(`  /${name}  ${description}`)
    }
  }
}
