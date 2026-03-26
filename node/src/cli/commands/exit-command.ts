import { Command } from '../service/command-registry.ts'

export class ExitCommand extends Command {
  get name() { return 'exit' }
  get description() { return 'Exit byte' }

  async execute(_args: string): Promise<void> {
    process.exit(0)
  }
}
