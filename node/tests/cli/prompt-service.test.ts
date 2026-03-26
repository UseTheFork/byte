import { describe, it, expect, mock } from 'bun:test'
import { PromptService } from '../../src/cli/service/prompt-service.ts'
import { ConsoleStore } from '../../src/cli/store/console-store.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'

function makeApp(store: ConsoleStore) {
  const handleMock = mock(async (_input: string) => {})
  const printMock = mock((_text: string, _style?: string) => {})
  const stopSpinnerMock = mock(() => {})
  const ruleMock = mock((_label?: string) => {})
  const emitMock = mock(async (p: unknown) => p)

  const mockConsole = {
    store,
    stopSpinner: stopSpinnerMock,
    rule: ruleMock,
    print: printMock,
  }
  const mockRegistry = { handle: handleMock }
  const mockEventBus = { emit: emitMock }

  const app: IApplication = {
    make: (key: unknown) => {
      if (key === 'console') return mockConsole as unknown
      if (key === 'event-bus') return mockEventBus as unknown
      return mockRegistry as unknown
    },
    singleton: () => {},
    bind: () => {},
    instance: () => undefined,
    running_unit_tests: () => true,
  }

  return { app, handleMock, printMock, stopSpinnerMock, ruleMock }
}

// Helper: run one loop iteration then stop
async function runOneIteration(
  service: PromptService,
  store: ConsoleStore,
  input: string,
): Promise<void> {
  const runPromise = service.run()
  // Yield to let the loop reach waitForSubmit
  await new Promise<void>((resolve) => setTimeout(resolve, 20))
  store.emit('submit', input)
  // Yield to let handler run
  await new Promise<void>((resolve) => setTimeout(resolve, 20))
  service.stop()
  // Unblock the next waitForSubmit so the loop can exit
  store.emit('submit', '')
  await runPromise
}

describe('PromptService routing', () => {
  it('routes /command input to command registry handle()', async () => {
    const store = new ConsoleStore()
    const { app, handleMock } = makeApp(store)
    const service = new PromptService(app)
    await runOneIteration(service, store, '/help')
    expect(handleMock).toHaveBeenCalledWith('/help')
  })

  it('routes /command with args to command registry handle()', async () => {
    const store = new ConsoleStore()
    const { app, handleMock } = makeApp(store)
    const service = new PromptService(app)
    await runOneIteration(service, store, '/exit foo')
    expect(handleMock).toHaveBeenCalledWith('/exit foo')
  })

  it('prints stub message for non-empty, non-command input', async () => {
    const store = new ConsoleStore()
    const { app, handleMock, printMock } = makeApp(store)
    const service = new PromptService(app)
    await runOneIteration(service, store, 'hello world')
    expect(handleMock).not.toHaveBeenCalled()
    expect(printMock).toHaveBeenCalled()
  })

  it('does nothing for empty input', async () => {
    const store = new ConsoleStore()
    const { app, handleMock, printMock } = makeApp(store)
    const service = new PromptService(app)

    const runPromise = service.run()
    await new Promise<void>((resolve) => setTimeout(resolve, 20))
    // First submit: empty (the actual test case)
    store.emit('submit', '   ')
    await new Promise<void>((resolve) => setTimeout(resolve, 20))
    service.stop()
    store.emit('submit', '')
    await runPromise

    expect(handleMock).not.toHaveBeenCalled()
    // print should NOT be called for empty/whitespace input
    // (stopSpinner and rule are always called)
    const printCallsForAgentStub = printMock.mock.calls.filter(
      ([text]) => typeof text === 'string' && text.includes('not yet')
    )
    expect(printCallsForAgentStub).toHaveLength(0)
  })

  it('stop() causes run() to resolve', async () => {
    const store = new ConsoleStore()
    const { app } = makeApp(store)
    const service = new PromptService(app)
    const runPromise = service.run()
    await new Promise<void>((resolve) => setTimeout(resolve, 20))
    service.stop()
    store.emit('submit', '')
    await expect(runPromise).resolves.toBeUndefined()
  })
})
