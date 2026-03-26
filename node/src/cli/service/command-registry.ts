import { Service } from '../../support/service.ts'
import type { IApplication } from '../../support/concerns/bootable.ts'

export abstract class Command {
  constructor(protected readonly app: IApplication) {}
  abstract get name(): string
  abstract get description(): string
  abstract execute(args: string): Promise<void>
  async getCompletions(_text: string): Promise<string[]> {
    return []
  }
}

export class CommandRegistry extends Service {
  static token = Symbol('CommandRegistry')

  private readonly _commands = new Map<string, Command>()

  register(command: Command): void {
    this._commands.set(command.name, command)
  }

  async handle(input: string): Promise<void> {
    const withoutSlash = input.slice(1)
    const spaceIdx = withoutSlash.indexOf(' ')
    const name = spaceIdx === -1 ? withoutSlash : withoutSlash.slice(0, spaceIdx)
    const args = spaceIdx === -1 ? '' : withoutSlash.slice(spaceIdx + 1)

    const command = this._commands.get(name)
    if (!command) {
      const console = this.app.make<{ printError(t: string): void }>('console')
      console.printError(`Unknown command: /${name}`)
      return
    }
    await command.execute(args)
  }

  getCompletions(text: string): [string, string][] {
    const prefix = text.startsWith('/') ? text.slice(1) : text
    const results: [string, string][] = []
    for (const [name, cmd] of this._commands) {
      if (name.startsWith(prefix)) {
        results.push([name, cmd.description])
      }
    }
    return results
  }
}
