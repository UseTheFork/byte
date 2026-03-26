# CLI Node/TS Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the byte CLI from Python (prompt_toolkit + Rich) to TypeScript (React + Ink), running under Bun, with a working REPL loop, /exit and /help commands, and all UI components.

**Architecture:** A `ConsoleStore` (EventEmitter) bridges imperative service calls to the Ink render tree. Services call `console.print()`, `console.startSpinner()` etc. without knowing about React. `<App>` subscribes to ConsoleStore's `'change'` event and re-renders on state changes. Agent execution is stubbed — the REPL loop prints a placeholder for plain text input.

**Tech Stack:** Bun, TypeScript strict, React + Ink (terminal renderer), chalk (styled text), marked + marked-terminal (markdown → ANSI).

---

## File Map

**New files to create:**

| File | Purpose |
|---|---|
| `node/src/cli/store/console-store.ts` | ConsoleStore: typed EventEmitter state bridge |
| `node/src/cli/service/console.ts` | Console: imperative API → ConsoleStore |
| `node/src/cli/service/command-registry.ts` | CommandRegistry + Command abstract base |
| `node/src/cli/commands/exit-command.ts` | `/exit` command |
| `node/src/cli/commands/help-command.ts` | `/help` command |
| `node/src/cli/service/interaction-service.ts` | InteractionService: confirm/select/inputText |
| `node/src/cli/service/stream-rendering-service.ts` | StreamRenderingService: no-op stub |
| `node/src/cli/service/prompt-service.ts` | PromptService: async REPL loop |
| `node/src/cli/components/theme.ts` | Catppuccin Mocha hex color map |
| `node/src/cli/components/byte-display.tsx` | `<ByteDisplay>`: ▌▌ bordered text |
| `node/src/cli/components/rune-spinner.tsx` | `<RuneSpinner>`: animated rune animation |
| `node/src/cli/components/menu.tsx` | `<Menu>`: keyboard-navigated select/confirm |
| `node/src/cli/components/markdown-stream.tsx` | `<MarkdownStream>`: live markdown rendering |
| `node/src/cli/components/prompt.tsx` | `<Prompt>`: input with history + completions |
| `node/src/cli/components/app.tsx` | `<App>`: top-level Ink component |
| `node/src/cli/service-provider.ts` | CLIServiceProvider |
| `node/src/cli/index.ts` | cli barrel |
| `node/src/main.ts` | entry point: bootstrap + ink render |
| `node/tests/cli/console-store.test.ts` | ConsoleStore tests |
| `node/tests/cli/command-registry.test.ts` | CommandRegistry tests |
| `node/tests/cli/interaction-service.test.ts` | InteractionService tests |
| `node/tests/cli/prompt-service.test.ts` | PromptService routing tests |

**Files to modify:**

| File | Change |
|---|---|
| `node/tsconfig.json` | Add `"jsx": "react-jsx"` |
| `node/package.json` | Add ink/react/chalk/marked deps + bin field |

---

## Task 1: Add Dependencies and Configure JSX

**Files:**
- Modify: `node/tsconfig.json`
- Modify: `node/package.json`

- [ ] **Step 1: Add jsx to tsconfig.json**

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "target": "ESNext",
    "module": "ESNext",
    "moduleDetection": "force",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "skipLibCheck": true,
    "types": ["bun-types"],
    "jsx": "react-jsx",
    "jsxImportSource": "react"
  },
  "include": ["src", "tests"]
}
```

- [ ] **Step 2: Install dependencies**

Run from `node/` directory:

```bash
cd node
bun add ink react marked marked-terminal chalk
bun add -d @types/react @types/marked-terminal
```

- [ ] **Step 3: Verify install succeeded**

```bash
cd node && bun test --bail
```

Expected: All existing tests still pass (no regressions from new deps).

- [ ] **Step 4: Commit**

```bash
cd node
git add tsconfig.json package.json bun.lockb
git commit -m "feat(cli): add ink/react/marked/chalk deps, enable JSX"
```

---

## Task 2: ConsoleStore

**Files:**
- Create: `node/src/cli/store/console-store.ts`
- Create: `node/tests/cli/console-store.test.ts`

- [ ] **Step 1: Write the failing test**

Create `node/tests/cli/console-store.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { ConsoleStore } from '../../src/cli/store/console-store.ts'

describe('ConsoleStore', () => {
  it('initialises with empty default state', () => {
    const store = new ConsoleStore()
    expect(store.state.messages).toEqual([])
    expect(store.state.spinner).toBeNull()
    expect(store.state.promptVisible).toBe(false)
    expect(store.state.promptDefault).toBe('')
    expect(store.state.modal).toBeNull()
    expect(store.state.live).toBeNull()
  })

  it('setState merges patch without mutating other fields', () => {
    const store = new ConsoleStore()
    store.setState({ promptVisible: true })
    expect(store.state.promptVisible).toBe(true)
    expect(store.state.messages).toEqual([])
    expect(store.state.spinner).toBeNull()
  })

  it('emits change event after setState', () => {
    const store = new ConsoleStore()
    let changeCount = 0
    store.on('change', () => { changeCount++ })
    store.setState({ promptVisible: true })
    expect(changeCount).toBe(1)
  })

  it('passes new state as argument to change listener', () => {
    const store = new ConsoleStore()
    let received: unknown
    store.on('change', (s) => { received = s })
    store.setState({ promptDefault: 'hello' })
    expect((received as { promptDefault: string }).promptDefault).toBe('hello')
  })

  it('appendMessage appends to messages and emits change', () => {
    const store = new ConsoleStore()
    let changeCount = 0
    store.on('change', () => { changeCount++ })
    store.appendMessage({ type: 'text', content: 'hello' })
    expect(store.state.messages).toHaveLength(1)
    expect(store.state.messages[0]).toEqual({ type: 'text', content: 'hello' })
    expect(changeCount).toBe(1)
  })

  it('appendMessage does not mutate previous messages array', () => {
    const store = new ConsoleStore()
    const before = store.state.messages
    store.appendMessage({ type: 'text', content: 'a' })
    expect(store.state.messages).not.toBe(before)
  })

  it('width defaults to 80 when process.stdout.columns is falsy', () => {
    const store = new ConsoleStore()
    expect(typeof store.state.width).toBe('number')
    expect(store.state.width).toBeGreaterThan(0)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd node && bun test tests/cli/console-store.test.ts
```

Expected: Error — cannot find module `../../src/cli/store/console-store.ts`

- [ ] **Step 3: Implement ConsoleStore**

Create `node/src/cli/store/console-store.ts`:

```typescript
import { EventEmitter } from 'events'

export type PrintItem =
  | { type: 'text'; content: string; style?: string }
  | { type: 'rule'; label?: string }
  | { type: 'error'; content: string }
  | { type: 'markdown'; content: string }

export interface SpinnerState {
  message: string
}

export interface LiveContent {
  content: string
  final: boolean
}

export interface ModalState {
  type: 'confirm' | 'select'
  message: string
  choices?: string[]
  default?: boolean | string
  resolve: (value: unknown) => void
}

export interface ConsoleState {
  messages: PrintItem[]
  spinner: SpinnerState | null
  promptVisible: boolean
  promptDefault: string
  modal: ModalState | null
  live: LiveContent | null
  width: number
}

export class ConsoleStore extends EventEmitter {
  private _state: ConsoleState = {
    messages: [],
    spinner: null,
    promptVisible: false,
    promptDefault: '',
    modal: null,
    live: null,
    width: process.stdout.columns ?? 80,
  }

  get state(): ConsoleState {
    return this._state
  }

  setState(patch: Partial<ConsoleState>): void {
    this._state = { ...this._state, ...patch }
    this.emit('change', this._state)
  }

  appendMessage(item: PrintItem): void {
    this.setState({ messages: [...this._state.messages, item] })
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd node && bun test tests/cli/console-store.test.ts
```

Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
cd node
git add src/cli/store/console-store.ts tests/cli/console-store.test.ts
git commit -m "feat(cli): add ConsoleStore EventEmitter state bridge"
```

---

## Task 3: Console Service

**Files:**
- Create: `node/src/cli/service/console.ts`

No unit test for Console — it's a thin wrapper over ConsoleStore whose behaviour is fully covered by ConsoleStore tests and integration via App.

- [ ] **Step 1: Implement Console service**

Create `node/src/cli/service/console.ts`:

```typescript
import { Service } from '../../support/service.ts'
import type { IApplication } from '../../support/concerns/bootable.ts'
import { ConsoleStore } from '../store/console-store.ts'

export class Console extends Service {
  static token = Symbol('Console')

  private readonly _store: ConsoleStore

  constructor(app: IApplication) {
    super(app)
    this._store = new ConsoleStore()
  }

  get store(): ConsoleStore {
    return this._store
  }

  get width(): number {
    return this._store.state.width
  }

  print(text: string, style?: string): void {
    this._store.appendMessage({ type: 'text', content: text, style })
  }

  rule(label?: string): void {
    this._store.appendMessage({ type: 'rule', label })
  }

  printError(text: string): void {
    this._store.appendMessage({ type: 'error', content: text })
  }

  startSpinner(message: string): void {
    this._store.setState({ spinner: { message } })
  }

  stopSpinner(): void {
    this._store.setState({ spinner: null })
  }

  clearLive(): void {
    this._store.setState({ live: null })
  }

  confirm(message: string, defaultValue = true): Promise<boolean> {
    return new Promise((resolve) => {
      this._store.setState({
        modal: {
          type: 'confirm',
          message,
          default: defaultValue,
          resolve: (v) => {
            this._store.setState({ modal: null })
            resolve(v as boolean)
          },
        },
      })
    })
  }

  select(message: string, ...choices: string[]): Promise<string> {
    return new Promise((resolve) => {
      this._store.setState({
        modal: {
          type: 'select',
          message,
          choices,
          resolve: (v) => {
            this._store.setState({ modal: null })
            resolve(v as string)
          },
        },
      })
    })
  }
}
```

- [ ] **Step 2: Run existing tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
cd node
git add src/cli/service/console.ts
git commit -m "feat(cli): add Console service wrapping ConsoleStore"
```

---

## Task 4: CommandRegistry and Command Base

**Files:**
- Create: `node/src/cli/service/command-registry.ts`
- Create: `node/tests/cli/command-registry.test.ts`

- [ ] **Step 1: Write the failing test**

Create `node/tests/cli/command-registry.test.ts`:

```typescript
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd node && bun test tests/cli/command-registry.test.ts
```

Expected: Error — cannot find module `../../src/cli/service/command-registry.ts`

- [ ] **Step 3: Implement CommandRegistry**

Create `node/src/cli/service/command-registry.ts`:

```typescript
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd node && bun test tests/cli/command-registry.test.ts
```

Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
cd node
git add src/cli/service/command-registry.ts tests/cli/command-registry.test.ts
git commit -m "feat(cli): add CommandRegistry and Command abstract base"
```

---

## Task 5: /exit and /help Commands

**Files:**
- Create: `node/src/cli/commands/exit-command.ts`
- Create: `node/src/cli/commands/help-command.ts`

No unit tests — trivially thin; `/exit` calls `process.exit(0)` which can't be unit tested without mocking, `/help` just calls `console.print()` which is covered implicitly.

- [ ] **Step 1: Implement /exit**

Create `node/src/cli/commands/exit-command.ts`:

```typescript
import { Command } from '../service/command-registry.ts'

export class ExitCommand extends Command {
  get name() { return 'exit' }
  get description() { return 'Exit byte' }

  async execute(_args: string): Promise<void> {
    process.exit(0)
  }
}
```

- [ ] **Step 2: Implement /help**

Create `node/src/cli/commands/help-command.ts`:

```typescript
import { Command } from '../service/command-registry.ts'
import type { CommandRegistry } from '../service/command-registry.ts'

export class HelpCommand extends Command {
  get name() { return 'help' }
  get description() { return 'Show available commands' }

  async execute(_args: string): Promise<void> {
    const registry = this.app.make<CommandRegistry>('command-registry')
    const console = this.app.make<{ print(t: string, style?: string): void }>('console')
    const completions = registry.getCompletions('')
    console.print('Available commands:', 'muted')
    for (const [name, description] of completions) {
      console.print(`  /${name}  ${description}`)
    }
  }
}
```

- [ ] **Step 3: Run existing tests to verify no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
cd node
git add src/cli/commands/exit-command.ts src/cli/commands/help-command.ts
git commit -m "feat(cli): add /exit and /help commands"
```

---

## Task 6: InteractionService

**Files:**
- Create: `node/src/cli/service/interaction-service.ts`
- Create: `node/tests/cli/interaction-service.test.ts`

- [ ] **Step 1: Write the failing test**

Create `node/tests/cli/interaction-service.test.ts`:

```typescript
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd node && bun test tests/cli/interaction-service.test.ts
```

Expected: Error — cannot find module `../../src/cli/service/interaction-service.ts`

- [ ] **Step 3: Implement InteractionService**

Create `node/src/cli/service/interaction-service.ts`:

```typescript
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd node && bun test tests/cli/interaction-service.test.ts
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
cd node
git add src/cli/service/interaction-service.ts tests/cli/interaction-service.test.ts
git commit -m "feat(cli): add InteractionService with confirm/select delegation"
```

---

## Task 7: StreamRenderingService Stub

**Files:**
- Create: `node/src/cli/service/stream-rendering-service.ts`

No tests — all methods are no-ops.

- [ ] **Step 1: Implement the stub**

Create `node/src/cli/service/stream-rendering-service.ts`:

```typescript
import { Service } from '../../support/service.ts'

export class StreamRenderingService extends Service {
  static token = Symbol('StreamRenderingService')

  async handleMessage(_chunk: unknown, _agentName: string): Promise<void> {}
  async startSpinner(_message?: string): Promise<void> {}
  async stopSpinner(): Promise<void> {}
  async endStream(): Promise<void> {}
  setDisplayMode(_mode: string): void {}
}
```

- [ ] **Step 2: Run existing tests to verify no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
cd node
git add src/cli/service/stream-rendering-service.ts
git commit -m "feat(cli): add StreamRenderingService stub"
```

---

## Task 8: PromptService

**Files:**
- Create: `node/src/cli/service/prompt-service.ts`
- Create: `node/tests/cli/prompt-service.test.ts`

- [ ] **Step 1: Write the failing test**

Create `node/tests/cli/prompt-service.test.ts`:

```typescript
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd node && bun test tests/cli/prompt-service.test.ts
```

Expected: Error — cannot find module `../../src/cli/service/prompt-service.ts`

- [ ] **Step 3: Implement PromptService**

Create `node/src/cli/service/prompt-service.ts`:

```typescript
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd node && bun test tests/cli/prompt-service.test.ts
```

Expected: 5 tests pass.

- [ ] **Step 5: Run all tests**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
cd node
git add src/cli/service/prompt-service.ts tests/cli/prompt-service.test.ts
git commit -m "feat(cli): add PromptService REPL loop with routing"
```

---

## Task 9: Theme, ByteDisplay, and RuneSpinner Components

**Files:**
- Create: `node/src/cli/components/theme.ts`
- Create: `node/src/cli/components/byte-display.tsx`
- Create: `node/src/cli/components/rune-spinner.tsx`

No unit tests — Ink components are verified manually at boot.

- [ ] **Step 1: Implement theme.ts**

Create `node/src/cli/components/theme.ts`:

```typescript
// Catppuccin Mocha palette mapped to semantic names.
// Source: foundation/console/console.py setup_console()
export const theme = {
  primary: '#89b4fa',        // base0D — blue (Functions, Headings)
  secondary: '#cba6f7',      // base0E — mauve (Keywords, Italic)
  muted: '#45475a',          // base03 — surface1 (Comments, Invisibles)
  error: '#f38ba8',          // base08 — red (Variables, Tags)
  text: '#cdd6f4',           // base05 — text (Default Foreground)
  active_border: '#b4befe',  // base07 — lavender (Light Background)
  inactive_border: '#45475a', // base03 — surface1 (Comments)
  danger: '#f38ba8',         // base08 — red
} as const

export type ThemeColor = keyof typeof theme
```

- [ ] **Step 2: Implement ByteDisplay**

Create `node/src/cli/components/byte-display.tsx`:

```tsx
import React from 'react'
import { Text, Box } from 'ink'
import chalk from 'chalk'
import { theme } from './theme.ts'

interface ByteDisplayProps {
  content: string
}

export function ByteDisplay({ content }: ByteDisplayProps): React.ReactElement {
  const lines = content.split('\n')
  const border =
    chalk.hex(theme.primary)('▌') + chalk.hex(theme.secondary)('▌')

  return (
    <Box flexDirection="column">
      {lines.map((line, i) => (
        <Text key={i}>
          {border}{line}
        </Text>
      ))}
    </Box>
  )
}
```

- [ ] **Step 3: Implement RuneSpinner**

Create `node/src/cli/components/rune-spinner.tsx`:

```tsx
import React, { useState, useEffect } from 'react'
import { Text, Box } from 'ink'
import chalk from 'chalk'
import { theme } from './theme.ts'

const RUNES = '0123456789abcdefABCDEF~!@#$%^&*()+=_'
const COLORS: (keyof typeof theme)[] = ['primary', 'secondary', 'text']
const SPINNER_SIZE = 6
const FRAME_INTERVAL_MS = 40

interface RuneSpinnerProps {
  message: string
}

export function RuneSpinner({ message }: RuneSpinnerProps): React.ReactElement {
  const [frame, setFrame] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setFrame((f) => f + 1)
    }, FRAME_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  const chars = Array.from({ length: SPINNER_SIZE }, (_, i) => {
    const runeSeed = (frame + i) * 31
    const colorSeed = (frame + i) * 37
    const rune = RUNES[runeSeed % RUNES.length] ?? '?'
    const colorName = COLORS[colorSeed % COLORS.length] ?? 'text'
    return chalk.hex(theme[colorName])(rune)
  }).join('')

  return (
    <Box>
      <Text>{chars}{message ? ` ${message}` : ''}</Text>
    </Box>
  )
}
```

- [ ] **Step 4: Run all tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass (components are not tested, just compiled).

- [ ] **Step 5: Commit**

```bash
cd node
git add src/cli/components/theme.ts src/cli/components/byte-display.tsx src/cli/components/rune-spinner.tsx
git commit -m "feat(cli): add theme, ByteDisplay, and RuneSpinner components"
```

---

## Task 10: Menu Component

**Files:**
- Create: `node/src/cli/components/menu.tsx`

No unit tests — verified manually at boot.

- [ ] **Step 1: Implement Menu component**

Create `node/src/cli/components/menu.tsx`:

```tsx
import React, { useState, useCallback } from 'react'
import { Text, Box, useInput } from 'ink'
import chalk from 'chalk'
import { theme } from './theme.ts'
import type { ModalState } from '../store/console-store.ts'

const WINDOW_SIZE = 5

interface MenuProps {
  modal: ModalState
}

export function Menu({ modal }: MenuProps): React.ReactElement {
  if (modal.type === 'confirm') {
    return <ConfirmMenu modal={modal} />
  }
  return <SelectMenu modal={modal} />
}

function ConfirmMenu({ modal }: MenuProps): React.ReactElement {
  const defaultIndex = modal.default === false ? 1 : 0
  const [index, setIndex] = useState(defaultIndex)
  const options = ['Yes', 'No']

  useInput(useCallback((input, key) => {
    if (key.leftArrow || input === 'h') {
      setIndex((i) => (i - 1 + options.length) % options.length)
    } else if (key.rightArrow || input === 'l') {
      setIndex((i) => (i + 1) % options.length)
    } else if (key.return) {
      modal.resolve(index === 0)
    } else if (key.escape) {
      modal.resolve(false)
    }
  }, [index, modal]))

  return (
    <Box flexDirection="column">
      <Text color={theme.text}>{modal.message}</Text>
      <Box gap={2}>
        {options.map((opt, i) => (
          <Text key={opt} color={i === index ? theme.primary : theme.muted}>
            {i === index ? '◼' : '◻'} {opt}
          </Text>
        ))}
      </Box>
    </Box>
  )
}

function SelectMenu({ modal }: MenuProps): React.ReactElement {
  const choices = modal.choices ?? []
  const [index, setIndex] = useState(0)
  const windowStart = Math.max(0, Math.min(index - Math.floor(WINDOW_SIZE / 2), choices.length - WINDOW_SIZE))
  const visible = choices.slice(windowStart, windowStart + WINDOW_SIZE)

  useInput(useCallback((input, key) => {
    if (key.upArrow || input === 'k') {
      setIndex((i) => (i - 1 + choices.length) % choices.length)
    } else if (key.downArrow || input === 'j') {
      setIndex((i) => (i + 1) % choices.length)
    } else if (key.return) {
      modal.resolve(choices[index] ?? '')
    } else if (key.escape) {
      modal.resolve(choices[0] ?? '')
    }
  }, [index, choices, modal]))

  return (
    <Box flexDirection="column">
      <Text color={theme.text}>{modal.message}</Text>
      {visible.map((choice, visIdx) => {
        const absIdx = windowStart + visIdx
        const isSelected = absIdx === index
        return (
          <Text key={choice} color={isSelected ? theme.primary : theme.muted}>
            {isSelected ? '›' : ' '} {choice}
          </Text>
        )
      })}
      {choices.length > WINDOW_SIZE && (
        <Text color={theme.muted}>
          ({index + 1}/{choices.length})
        </Text>
      )}
    </Box>
  )
}
```

- [ ] **Step 2: Run all tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
cd node
git add src/cli/components/menu.tsx
git commit -m "feat(cli): add Menu component for confirm/select dialogs"
```

---

## Task 11: MarkdownStream Component

**Files:**
- Create: `node/src/cli/components/markdown-stream.tsx`

No unit tests — verified manually at boot.

- [ ] **Step 1: Implement MarkdownStream**

Create `node/src/cli/components/markdown-stream.tsx`:

```tsx
import React, { useMemo } from 'react'
import { Text, Box } from 'ink'
import { marked } from 'marked'
// @ts-expect-error marked-terminal has no bundled types
import TerminalRenderer from 'marked-terminal'
import { ByteDisplay } from './byte-display.tsx'
import type { LiveContent } from '../store/console-store.ts'

// Pre-process agent_plan and operation_block tags — mirrors Python _preprocess_tags
function preprocessTags(content: string): string {
  return content
    .replace(/<agent_plan>([\s\S]*?)<\/agent_plan>/g, '\n```byte\n$1\n```\n')
    .replace(/<operation_block>([\s\S]*?)<\/operation_block>/g, '\n```byte\n$1\n```\n')
}

interface MarkdownStreamProps {
  live: LiveContent
}

export function MarkdownStream({ live }: MarkdownStreamProps): React.ReactElement {
  const rendered = useMemo(() => {
    marked.setOptions({ renderer: new TerminalRenderer() })
    const preprocessed = preprocessTags(live.content)
    return marked.parse(preprocessed) as string
  }, [live.content])

  // Split on ```byte blocks to render them with ByteDisplay
  const parts = rendered.split(/(```byte[\s\S]*?```)/g)

  return (
    <Box flexDirection="column">
      {parts.map((part, i) => {
        if (part.startsWith('```byte')) {
          const inner = part.replace(/^```byte\n?/, '').replace(/\n?```$/, '')
          return <ByteDisplay key={i} content={inner} />
        }
        return <Text key={i}>{part}</Text>
      })}
    </Box>
  )
}
```

- [ ] **Step 2: Run all tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
cd node
git add src/cli/components/markdown-stream.tsx
git commit -m "feat(cli): add MarkdownStream component with tag preprocessing"
```

---

## Task 12: Prompt Component

**Files:**
- Create: `node/src/cli/components/prompt.tsx`

No unit tests — verified manually at boot.

- [ ] **Step 1: Implement Prompt**

Create `node/src/cli/components/prompt.tsx`:

```tsx
import React, { useState, useEffect, useCallback } from 'react'
import { Text, Box, useInput } from 'ink'
import { readFileSync, appendFileSync } from 'fs'
import chalk from 'chalk'
import { theme } from './theme.ts'
import type { ConsoleStore } from '../store/console-store.ts'

function loadHistory(historyPath: string): string[] {
  try {
    const content = readFileSync(historyPath, 'utf-8')
    return content.split('\n').filter(Boolean).reverse()
  } catch {
    return []
  }
}

function saveToHistory(historyPath: string, input: string): void {
  try {
    appendFileSync(historyPath, input + '\n')
  } catch {
    // ignore — cache dir may not exist yet
  }
}

interface PromptProps {
  store: ConsoleStore
  historyPath: string
  onConfirmQuit: () => Promise<boolean>
}

export function Prompt({ store, historyPath, onConfirmQuit }: PromptProps): React.ReactElement {
  const [buffer, setBuffer] = useState(store.state.promptDefault)
  const [history] = useState<string[]>(() => loadHistory(historyPath))
  const [historyIndex, setHistoryIndex] = useState(-1)

  // Reset buffer when promptDefault changes (interrupt-restore)
  useEffect(() => {
    setBuffer(store.state.promptDefault)
  }, [store.state.promptDefault])

  useInput(useCallback((input, key) => {
    if (key.return) {
      const value = buffer
      setBuffer('')
      setHistoryIndex(-1)
      if (value.trim()) {
        saveToHistory(historyPath, value)
      }
      store.emit('submit', value)
      return
    }

    if (key.ctrl && input === 'c') {
      void onConfirmQuit().then((confirmed) => {
        if (confirmed) process.exit(0)
      })
      return
    }

    if (key.backspace || key.delete) {
      setBuffer((b) => b.slice(0, -1))
      return
    }

    if (key.upArrow) {
      const next = Math.min(historyIndex + 1, history.length - 1)
      setHistoryIndex(next)
      setBuffer(history[next] ?? '')
      return
    }

    if (key.downArrow) {
      const next = historyIndex - 1
      if (next < 0) {
        setHistoryIndex(-1)
        setBuffer('')
      } else {
        setHistoryIndex(next)
        setBuffer(history[next] ?? '')
      }
      return
    }

    // Tab: emit 'tab' on store so PromptService can handle completion
    if (key.tab && buffer.startsWith('/')) {
      store.emit('tab', buffer)
      return
    }

    // Alt+Enter: newline in buffer
    if (key.meta && key.return) {
      setBuffer((b) => b + '\n')
      return
    }

    // Printable characters
    if (input && !key.ctrl && !key.meta) {
      setBuffer((b) => b + input)
    }
  }, [buffer, historyIndex, history, historyPath, store, onConfirmQuit]))

  const cursor = chalk.hex(theme.primary)('❯ ')

  return (
    <Box>
      <Text>{cursor}{buffer}</Text>
    </Box>
  )
}
```

- [ ] **Step 2: Run all tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
cd node
git add src/cli/components/prompt.tsx
git commit -m "feat(cli): add Prompt component with history and key bindings"
```

---

## Task 13: App Component

**Files:**
- Create: `node/src/cli/components/app.tsx`

No unit tests — verified manually at boot.

- [ ] **Step 1: Implement App**

Create `node/src/cli/components/app.tsx`:

```tsx
import React, { useState, useEffect, useCallback } from 'react'
import { Text, Box } from 'ink'
import { theme } from './theme.ts'
import { RuneSpinner } from './rune-spinner.tsx'
import { Menu } from './menu.tsx'
import { Prompt } from './prompt.tsx'
import { MarkdownStream } from './markdown-stream.tsx'
import type { Console } from '../service/console.ts'
import type { PromptService } from '../service/prompt-service.ts'
import type { ConsoleState, PrintItem } from '../store/console-store.ts'

interface AppProps {
  consoleService: Console
  promptService: PromptService
  cachePath: string
}

function renderPrintItem(item: PrintItem, index: number): React.ReactElement {
  switch (item.type) {
    case 'text':
      return (
        <Text key={index} color={item.style ? theme[item.style as keyof typeof theme] ?? theme.text : theme.text}>
          {item.content}
        </Text>
      )
    case 'error':
      return <Text key={index} color={theme.error}>{item.content}</Text>
    case 'rule':
      return (
        <Text key={index} color={theme.muted}>
          {item.label
            ? `─── ${item.label} ${'─'.repeat(Math.max(0, (process.stdout.columns ?? 80) - item.label.length - 5))}`
            : '─'.repeat(process.stdout.columns ?? 80)}
        </Text>
      )
    case 'markdown':
      return <Text key={index}>{item.content}</Text>
    default:
      return <Text key={index}>{(item as { content?: string }).content ?? ''}</Text>
  }
}

export function App({ consoleService, promptService, cachePath }: AppProps): React.ReactElement {
  const [state, setState] = useState<ConsoleState>(consoleService.store.state)

  useEffect(() => {
    const handler = (newState: ConsoleState) => setState(newState)
    consoleService.store.on('change', handler)

    // Start the REPL loop — fire and forget
    void promptService.run()

    return () => {
      consoleService.store.off('change', handler)
    }
  }, [consoleService, promptService])

  const historyPath = cachePath + '/.input_history'

  const onConfirmQuit = useCallback(
    () => consoleService.confirm('Do you want to quit?'),
    [consoleService],
  )

  return (
    <Box flexDirection="column">
      {/* Past messages */}
      {state.messages.map((item, i) => renderPrintItem(item, i))}

      {/* One active element */}
      {state.spinner && <RuneSpinner message={state.spinner.message} />}
      {state.live && !state.spinner && <MarkdownStream live={state.live} />}
      {state.modal && !state.spinner && (
        <Menu modal={state.modal} />
      )}
      {state.promptVisible && !state.spinner && !state.modal && (
        <Prompt
          store={consoleService.store}
          historyPath={historyPath}
          onConfirmQuit={onConfirmQuit}
        />
      )}
    </Box>
  )
}
```

- [ ] **Step 2: Run all tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
cd node
git add src/cli/components/app.tsx
git commit -m "feat(cli): add App component subscribing to ConsoleStore"
```

---

## Task 14: Fix Application.register(), then CLIServiceProvider and cli/index.ts Barrel

**Files:**
- Modify: `node/src/foundation/application.ts` (add `addProvider` call in `register()`)
- Modify: `node/tests/foundation/integration.test.ts` (add boot() test)
- Create: `node/src/cli/service-provider.ts`
- Create: `node/src/cli/index.ts`

**Why the Application fix is here:** `Application.register()` calls `provider.register()` and `provider.registerServices()` but never calls `this.addProvider(provider)`. This means `app.boot()` iterates an empty `_registeredProviders` list and never calls any provider's `boot()` method. `CLIServiceProvider.boot()` registers commands and the logo event listener — it must run.

- [ ] **Step 1: Write a failing test for provider boot()**

Add to `node/tests/foundation/integration.test.ts`:

```typescript
it('app.boot() calls boot() on registered providers', async () => {
  let booted = false

  class TrackingProvider extends ServiceProvider {
    override register(): void {}
    override async boot(): Promise<void> {
      booted = true
    }
  }

  const app = Application.configure(testBasePath)
    .withProviders([TrackingProvider as never])
    .create()

  expect(booted).toBe(false)
  await app.boot()
  expect(booted).toBe(true)
})
```

Run to verify it fails:

```bash
cd node && bun test tests/foundation/integration.test.ts
```

Expected: FAIL — `booted` is never set to `true`.

- [ ] **Step 2: Fix Application.register() to call addProvider()**

Edit `node/src/foundation/application.ts`, change the `register` method from:

```typescript
register(ProviderClass: Newable<ServiceProvider>): ServiceProvider {
  this.singleton(ProviderClass as never, () => new ProviderClass(this))
  const provider = this.make(ProviderClass as never) as ServiceProvider
  provider.register()
  provider.registerServices()
  return provider
}
```

to:

```typescript
register(ProviderClass: Newable<ServiceProvider>): ServiceProvider {
  this.singleton(ProviderClass as never, () => new ProviderClass(this))
  const provider = this.make(ProviderClass as never) as ServiceProvider
  provider.register()
  provider.registerServices()
  this.addProvider(provider)
  return provider
}
```

- [ ] **Step 3: Run all tests to verify the fix**

```bash
cd node && bun test
```

Expected: All tests pass including the new boot() test.

- [ ] **Step 4: Commit the fix**

```bash
cd node
git add src/foundation/application.ts tests/foundation/integration.test.ts
git commit -m "fix(foundation): Application.register() now calls addProvider() so boot() runs on providers"
```

- [ ] **Step 5: Implement CLIServiceProvider**

Create `node/src/cli/service-provider.ts`:

```typescript
import { ServiceProvider } from '../support/service-provider.ts'
import { Console } from './service/console.ts'
import { PromptService } from './service/prompt-service.ts'
import { CommandRegistry } from './service/command-registry.ts'
import { InteractionService } from './service/interaction-service.ts'
import { StreamRenderingService } from './service/stream-rendering-service.ts'
import { ExitCommand } from './commands/exit-command.ts'
import { HelpCommand } from './commands/help-command.ts'
import { EventBus, EventType } from '../foundation/event-bus.ts'
import { Payload } from '../support/concerns/eventable.ts'

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
```

- [ ] **Step 2: Create cli/index.ts barrel**

Create `node/src/cli/index.ts`:

```typescript
export { CLIServiceProvider } from './service-provider.ts'
export { Console } from './service/console.ts'
export { PromptService } from './service/prompt-service.ts'
export { CommandRegistry, Command } from './service/command-registry.ts'
export { InteractionService, InputCancelledError } from './service/interaction-service.ts'
export { StreamRenderingService } from './service/stream-rendering-service.ts'
export { ConsoleStore } from './store/console-store.ts'
export type { ConsoleState, PrintItem, ModalState, SpinnerState, LiveContent } from './store/console-store.ts'
export { App } from './components/app.tsx'
export { theme } from './components/theme.ts'
```

- [ ] **Step 3: Run all tests to ensure no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
cd node
git add src/cli/service-provider.ts src/cli/index.ts
git commit -m "feat(cli): add CLIServiceProvider and cli barrel"
```

---

## Task 15: Entry Point and Boot Verification

**Files:**
- Create: `node/src/main.ts`
- Modify: `node/package.json` (add bin field)

- [ ] **Step 1: Implement main.ts**

Create `node/src/main.ts`:

```typescript
import React from 'react'
import { render } from 'ink'
import { Application } from './foundation/application.ts'
import { FoundationServiceProvider } from './foundation/service-provider.ts'
import { CLIServiceProvider } from './cli/service-provider.ts'
import { Console } from './cli/service/console.ts'
import { PromptService } from './cli/service/prompt-service.ts'
import { App } from './cli/components/app.tsx'

const app = Application.configure(process.cwd(), [
  FoundationServiceProvider as never,
  CLIServiceProvider as never,
]).create()

await app.boot()

const consoleService = app.make<Console>('console')
const promptService = app.make<PromptService>(PromptService as never)
const cachePath = app.make<string>('path.cache')

render(React.createElement(App, { consoleService, promptService, cachePath }))
```

- [ ] **Step 2: Add bin field to package.json**

Edit `node/package.json` to add the `bin` field and a `dev` script:

```json
{
  "name": "byte-node",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "bin": {
    "byte": "./src/main.ts"
  },
  "scripts": {
    "start": "bun run src/main.ts",
    "dev": "bun run src/main.ts",
    "test": "bun test"
  },
  "dependencies": {
    "chalk": "^5.4.1",
    "ink": "^5.1.0",
    "js-yaml": "^4.1.0",
    "marked": "^15.0.0",
    "marked-terminal": "^7.3.0",
    "react": "^18.3.1",
    "simple-git": "^3.27.0"
  },
  "devDependencies": {
    "@types/js-yaml": "^4.0.9",
    "@types/marked-terminal": "^6.1.0",
    "@types/react": "^18.3.18",
    "bun-types": "latest",
    "typescript": "^5.7.0"
  }
}
```

Note: exact versions will be whatever `bun add` installed in Task 1. Do not change version numbers here — only add the `bin` field and `dev` script.

- [ ] **Step 3: Run all tests to verify nothing is broken**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 4: Boot verification — start the CLI**

```bash
cd node && bun run src/main.ts
```

Expected:
- Terminal clears and renders the byte logo (░▒▓█ gradient)
- Version and Project Root lines display in muted colour
- A horizontal rule appears: `─── ▌▌ Byte ───`
- The `❯ ` prompt cursor appears, ready for input
- `/help` lists `/exit` and `/help` commands
- `/exit` terminates the process
- Ctrl+C shows a "Do you want to quit?" Yes/No menu

If the CLI boots and accepts input correctly, proceed to commit.

- [ ] **Step 5: Commit**

```bash
cd node
git add src/main.ts package.json
git commit -m "feat(cli): add main.ts entry point, wire CLIServiceProvider to Ink"
```

---

## Final Verification

After Task 15:

```bash
cd node && bun test
```

Expected: All tests pass (existing foundation/support tests + new cli tests).

Manual smoke test checklist:
- [ ] Logo renders with gradient
- [ ] `/help` shows command table
- [ ] `/exit` terminates
- [ ] Unknown command shows error in error colour
- [ ] Ctrl+C shows confirm dialog; cancelling returns to prompt
- [ ] Up/Down arrows cycle input history
- [ ] Plain text input shows "Agent execution not yet implemented."
