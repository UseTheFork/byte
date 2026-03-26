import { describe, it, expect, mock } from 'bun:test'
import { InteractionService, InputCancelledError } from '../../src/cli/service/interaction-service.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

function makeApp(consoleMethods: {
  confirm?: (msg: string, def?: boolean) => Promise<boolean>
  select?: (msg: string, ...choices: string[]) => Promise<string>
}): IApplication {
  return {
    make: (_key: unknown) => consoleMethods as unknown,
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  }
}

describe('InteractionService', () => {
  it('confirm delegates to console.confirm with message and default', async () => {
    const confirmMock = mock(async (_msg: string, _def?: boolean) => true)
    const app = makeApp({ confirm: confirmMock })
    const service = new InteractionService(app)
    const result = await service.confirm('Are you sure?', false)
    expect(result).toBe(true)
    expect(confirmMock).toHaveBeenCalledWith('Are you sure?', false)
  })

  it('confirm defaults to true when no default provided', async () => {
    const confirmMock = mock(async (_msg: string, _def?: boolean) => false)
    const app = makeApp({ confirm: confirmMock })
    const service = new InteractionService(app)
    await service.confirm('Sure?')
    expect(confirmMock).toHaveBeenCalledWith('Sure?', true)
  })

  it('select delegates to console.select with message and spread choices', async () => {
    const selectMock = mock(async (..._args: unknown[]) => 'Option A')
    const app = makeApp({ select: selectMock as never })
    const service = new InteractionService(app)
    const result = await service.select('Pick one', ['Option A', 'Option B'])
    expect(result).toBe('Option A')
    expect(selectMock).toHaveBeenCalledWith('Pick one', 'Option A', 'Option B')
  })

  it('InputCancelledError is an Error', () => {
    const err = new InputCancelledError()
    expect(err).toBeInstanceOf(Error)
    expect(err.message).toBe('Input cancelled')
  })
})
