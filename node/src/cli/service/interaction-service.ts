import { Service } from '../../support/service.ts'

export class InputCancelledError extends Error {
  constructor() {
    super('Input cancelled')
    this.name = 'InputCancelledError'
  }
}

interface ConsoleApi {
  confirm(message: string, defaultValue?: boolean): Promise<boolean>
  select(message: string, ...choices: string[]): Promise<string>
}

export class InteractionService extends Service {
  static token = Symbol('InteractionService')

  private get _console(): ConsoleApi {
    return this.app.make<ConsoleApi>('console')
  }

  async confirm(message: string, defaultValue = true): Promise<boolean> {
    return this._console.confirm(message, defaultValue)
  }

  async select(message: string, choices: string[], _default?: string): Promise<string> {
    return this._console.select(message, ...choices)
  }

  // Full implementation pending agent domain migration.
  async inputText(_message: string, _default?: string): Promise<string> {
    throw new InputCancelledError()
  }
}
