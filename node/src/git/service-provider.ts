import { ServiceProvider } from '../support/service-provider.ts'
import type { CommandRegistry } from '../cli/service/command-registry.ts'
import { GitService } from './service/git-service.ts'
import { CommitService } from './service/commit-service.ts'
import { CommitCommand } from './command/commit-command.ts'

export class GitServiceProvider extends ServiceProvider {
  override register(): void {
    this.app.singleton(GitService as never, () => {
      const svc = new GitService(this.app)
      svc.ensureBooted()
      return svc
    })
    this.app.singleton(CommitService as never, () => {
      const svc = new CommitService(this.app)
      svc.ensureBooted()
      return svc
    })
  }

  override async boot(): Promise<void> {
    const registry = this.app.make<CommandRegistry>('command-registry')
    registry.register(new CommitCommand(this.app))
  }
}
