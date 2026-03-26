import { ServiceProvider } from '../support/service-provider.ts'
import { Console } from './service/console.ts'
import { PromptService } from './service/prompt-service.ts'
import { CommandRegistry } from './service/command-registry.ts'
import { InteractionService } from './service/interaction-service.ts'
import { StreamRenderingService } from './service/stream-rendering-service.ts'
import { ExitCommand } from './commands/exit-command.ts'
import { HelpCommand } from './commands/help-command.ts'
import { EventBus, EventType } from '../foundation/event-bus.ts'
import type { Payload } from '../support/concerns/eventable.ts'

export class CLIServiceProvider extends ServiceProvider {
  // All registration is manual (needs custom factories) — services() stays as the base [] default.

  override register(): void {
    // Console: registered with both class token and 'console' string key
    this.app.singleton(Console as never, () => new Console(this.app))
    this.app.instance('console', this.app.make(Console as never))

    // CommandRegistry: registered with both class token and 'command-registry' string key
    this.app.singleton(CommandRegistry as never, () => new CommandRegistry(this.app))
    this.app.instance('command-registry', this.app.make(CommandRegistry as never))

    this.app.singleton(PromptService as never, () => new PromptService(this.app))
    this.app.singleton(InteractionService as never, () => new InteractionService(this.app))
    this.app.singleton(StreamRenderingService as never, () => new StreamRenderingService(this.app))
  }

  override async boot(): Promise<void> {
    const registry = this.app.make<CommandRegistry>('command-registry')
    registry.register(new ExitCommand(this.app))
    registry.register(new HelpCommand(this.app))

    const eventBus = this.app.make<EventBus>('event-bus')
    eventBus.on(EventType.POST_BOOT, this.bootMessages.bind(this))
  }

  async bootMessages(payload: Payload): Promise<Payload> {
    const console = this.app.make<Console>('console')
    const version = '0.3.0'
    const rootPath = this.app.make<string>('path.root')

    const logoLines = [
      '░       ░░░  ░░░░  ░░        ░░        ░',
      '▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒',
      '▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓',
      '█  ████  █████  ████████  █████  ███████',
      '█       ██████  ████████  █████        █',
    ]

    const totalDiag = logoLines.length + (logoLines[0]?.length ?? 0) - 2

    for (let row = 0; row < logoLines.length; row++) {
      const line = logoLines[row] ?? ''
      let styled = ''
      for (let col = 0; col < line.length; col++) {
        const progress = (row + col) / totalDiag
        styled += progress < 0.5 ? `\x1b[38;2;137;180;250m${line[col]}\x1b[0m` : `\x1b[38;2;203;166;247m${line[col]}\x1b[0m`
      }
      console.print(styled)
    }

    console.print('')
    console.print(`Version: ${version}`, 'muted')
    console.print(`Project Root: ${rootPath}`, 'muted')

    return payload
  }
}
