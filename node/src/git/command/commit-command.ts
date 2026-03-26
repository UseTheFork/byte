import { Command } from '../../cli/service/command-registry.ts'

export class CommitCommand extends Command {
  get name() { return 'commit' }
  get description() { return 'Create a conventional commit (coming soon)' }

  async execute(_args: string): Promise<void> {
    this.app.make<{ print(msg: string): void }>('console').print('not yet implemented')
  }
}
