import { Service } from '../../support/service.ts'
import { Payload } from '../../support/concerns/eventable.ts'
import { EventType } from '../../foundation/event-bus.ts'
import type { ConsoleStore } from '../store/console-store.ts'
import type { CommandRegistry } from './command-registry.ts'

interface ConsoleApi {
  store: ConsoleStore
  stopSpinner(): void
  rule(label?: string): void
  print(text: string, style?: string): void
}

export class PromptService extends Service {
  static token = Symbol('PromptService')

  private _running = false

  private get _console(): ConsoleApi {
    return this.app.make<ConsoleApi>('console')
  }

  private get _store(): ConsoleStore {
    return this._console.store
  }

  private get _registry(): CommandRegistry {
    return this.app.make<CommandRegistry>('command-registry')
  }

  private waitForSubmit(): Promise<string> {
    return new Promise((resolve) => {
      this._store.once('submit', resolve as (value: unknown) => void)
    })
  }

  async run(): Promise<void> {
    this._running = true

    // Emit POST_BOOT — triggers CLIServiceProvider.bootMessages
    const eventBus = this.app.make<{ emit(p: Payload): Promise<Payload> }>('event-bus')
    await eventBus.emit(new Payload(EventType.POST_BOOT))

    while (this._running) {
      const console = this._console
      console.stopSpinner()
      console.rule('▌▌ Byte')
      this._store.setState({ promptVisible: true })

      const input = await this.waitForSubmit()

      this._store.setState({ promptVisible: false })

      if (!this._running) break

      if (input.startsWith('/')) {
        await this._registry.handle(input)
      } else if (input.trim() !== '') {
        console.print('Agent execution not yet implemented.', 'muted')
      }
      // empty input: no-op
    }
  }

  stop(): void {
    this._running = false
  }
}
