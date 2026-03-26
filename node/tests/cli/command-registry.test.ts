import { describe, it, expect, mock } from 'bun:test'
import { CommandRegistry, Command } from '../../src/cli/service/command-registry.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const printErrorMock = mock((_msg: string) => {})

const mockApp: IApplication = {
  make: (_key: unknown) => ({ printError: printErrorMock }) as unknown,
  singleton: () => {},
  bind: () => {},
  instance: () => undefined,
  running_unit_tests: () => true,
}

class EchoCommand extends Command {
  readonly calls: string[] = []
  get name() { return 'echo' }
  get description() { return 'echoes args' }
  async execute(args: string): Promise<void> {
    this.calls.push(args)
  }
}

describe('CommandRegistry', () => {
  it('handle routes to registered command with args', async () => {
    const registry = new CommandRegistry(mockApp)
    const cmd = new EchoCommand(mockApp)
    registry.register(cmd)
    await registry.handle('/echo hello world')
    expect(cmd.calls).toEqual(['hello world'])
  })

  it('handle routes command with no args', async () => {
    const registry = new CommandRegistry(mockApp)
    const cmd = new EchoCommand(mockApp)
    registry.register(cmd)
    await registry.handle('/echo')
    expect(cmd.calls).toEqual([''])
  })

  it('handle calls printError for unknown command', async () => {
    const registry = new CommandRegistry(mockApp)
    printErrorMock.mockClear()
    await registry.handle('/unknown')
    expect(printErrorMock).toHaveBeenCalledWith('Unknown command: /unknown')
  })

  it('getCompletions returns prefix-matched commands', () => {
    const registry = new CommandRegistry(mockApp)
    registry.register(new EchoCommand(mockApp))
    const results = registry.getCompletions('ec')
    expect(results).toEqual([['echo', 'echoes args']])
  })

  it('getCompletions returns all when prefix is empty', () => {
    const registry = new CommandRegistry(mockApp)
    registry.register(new EchoCommand(mockApp))
    const results = registry.getCompletions('')
    expect(results).toHaveLength(1)
  })

  it('getCompletions returns empty for no match', () => {
    const registry = new CommandRegistry(mockApp)
    registry.register(new EchoCommand(mockApp))
    const results = registry.getCompletions('xyz')
    expect(results).toEqual([])
  })

  it('Command default getCompletions returns empty array', async () => {
    const cmd = new EchoCommand(mockApp)
    const completions = await cmd.getCompletions('anything')
    expect(completions).toEqual([])
  })
})
