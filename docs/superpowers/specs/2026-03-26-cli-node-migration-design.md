# Design: CLI Domain — Python to Node/TS Migration

**Date:** 2026-03-26
**Branch:** dev-v3-node
**Scope:** `cli` domain — entry point (`main.ts`), `CLIServiceProvider`, `Console` service, `PromptService` (REPL loop), `CommandRegistry`, `InteractionService`, `StreamRenderingService` (stub), Ink UI components. Agent execution is deferred — the REPL loop stubs agent calls. Python source is preserved and serves as the reference implementation.

---

## Overview

Port the CLI layer of the byte CLI from Python (prompt_toolkit + Rich) to TypeScript (React + Ink), running under Bun. The Node binary becomes the actual `byte` entry point. The Python side remains intact as a reference.

The UI is built with **React + Ink** (terminal React renderer). The service layer stays imperative — services call `console.print()`, `console.startSpinner()`, etc. as in Python. A **ConsoleStore** (typed reactive state + EventEmitter) bridges the imperative service calls to the Ink render tree without React leaking into the service layer.

---

## Tooling Additions

| Concern | Choice |
|---|---|
| Terminal UI | `ink` + `react` |
| Markdown → ANSI | `marked` + `marked-terminal` |
| Styled text | `chalk` (Ink's internal dependency, re-used) |
| Types | `@types/react` |

---

## Repository Layout

```
node/src/
  main.ts                              ← entry point: bootstrap + ink render
  cli/
    index.ts                           ← barrel
    service-provider.ts                ← CLIServiceProvider
    store/
      console-store.ts                 ← ConsoleStore: typed state + EventEmitter
    service/
      console.ts                       ← Console: imperative API → store
      prompt-service.ts                ← PromptService: REPL loop
      command-registry.ts              ← CommandRegistry + Command base class
      interaction-service.ts           ← InteractionService: confirm/select/input
      stream-rendering-service.ts      ← StreamRenderingService: stub
    commands/
      exit-command.ts                  ← /exit
      help-command.ts                  ← /help
    components/
      app.tsx                          ← <App>: top-level Ink component
      prompt.tsx                       ← <Prompt>: input with history + completion
      rune-spinner.tsx                 ← <RuneSpinner>: animated rune animation
      menu.tsx                         ← <Menu>: keyboard-navigated select/confirm
      byte-display.tsx                 ← <ByteDisplay>: ▌▌ bordered text
      markdown-stream.tsx              ← <MarkdownStream>: live markdown rendering
      theme.ts                         ← named colour → hex mapping
  tests/
    cli/
      console-store.test.ts
      command-registry.test.ts
      interaction-service.test.ts
      prompt-service.test.ts
```

---

## Architecture

### ConsoleStore (Reactive Bridge)

`ConsoleStore` extends `EventEmitter`. Holds all terminal UI state. `setState(patch)` merges the patch and emits `'change'`. The Ink `<App>` subscribes to `'change'` via `useEffect` and calls `React.setState` to trigger re-renders.

```typescript
interface ConsoleState {
  messages: PrintItem[]        // history — appended, never mutated in place
  spinner: SpinnerState | null // null = no spinner
  promptVisible: boolean       // true = render <Prompt>
  promptDefault: string        // pre-filled input on interrupt-restore
  modal: ModalState | null     // active confirm/select dialog
  live: LiveContent | null     // streaming markdown (agent — future)
  width: number                // process.stdout.columns at boot
}

type PrintItem =
  | { type: 'text';     content: string; style?: string }
  | { type: 'rule';     label?: string }
  | { type: 'error';    content: string }
  | { type: 'markdown'; content: string }

interface SpinnerState  { message: string }
interface LiveContent   { content: string; final: boolean }

interface ModalState {
  type: 'confirm' | 'select'
  message: string
  choices?: string[]
  default?: boolean | string
  resolve: (value: unknown) => void
}
```

`ConsoleStore` also emits a `'submit'` event when the user submits input from `<Prompt>`. `PromptService.waitForSubmit()` registers a one-shot listener and returns `Promise<string>`.

---

### Console Service

DI singleton (token: `'console'`). Wraps `ConsoleStore` with an imperative API:

| Method | Effect |
|---|---|
| `print(text, style?)` | Append text `PrintItem` |
| `rule(label?)` | Append rule `PrintItem` |
| `printError(text)` | Append error `PrintItem` |
| `startSpinner(message)` | Set spinner state |
| `stopSpinner()` | Clear spinner |
| `clearLive()` | Clear live content |
| `confirm(message, default?)` | Set modal state, return `Promise<boolean>` |
| `select(...choices)` | Set modal state, return `Promise<string>` |

`confirm()` and `select()` create a `ModalState` with an inline `resolve` callback and return a `Promise`. The `<Menu>` Ink component calls `modal.resolve(value)` on selection, clearing the modal and resolving the promise.

`width` is populated from `process.stdout.columns` at construction time.

---

### Ink `<App>` Component

Mounts once at boot. Receives `console` and `promptService` as props from `main.ts`. Subscribes to `ConsoleStore` via `useState`/`useEffect`.

Render structure:
```
past messages (PrintItems)     ← static history
  <Text> / <Rule> / <Markdown>

[one active element:]
  <RuneSpinner>                ← if spinner !== null
  <MarkdownStream>             ← if live !== null
  <Menu>                       ← if modal !== null
  <Prompt>                     ← if promptVisible
```

Only one active element renders at a time. On mount, a `useEffect` calls `promptService.run()` without awaiting — the async REPL loop runs independently of the React render cycle. `<Prompt>` receives the history file path as a prop (sourced from `app.make<string>('path.cache')` in `main.ts`).

---

### REPL Loop (`PromptService`)

```
1. Emit POST_BOOT event → boot messages appended to store
2. Loop:
   a. console.stopSpinner()
   b. console.rule('▌▌ Byte')
   c. store.setState({ promptVisible: true })
   d. input = await waitForSubmit()
   e. store.setState({ promptVisible: false })
   f. Route:
      - input.startsWith('/')  → commandRegistry.handle(input)
      - input.trim() !== ''    → agentStub.execute(input)
      - else                   → no-op
   g. goto 2
```

`waitForSubmit()` returns `Promise<string>` via a one-shot `'submit'` EventEmitter listener on the store.

---

### `<Prompt>` Component

Uses Ink's `useInput` hook. Receives `historyPath: string` as a prop (from `cachePath + '/.input_history'`). Maintains `buffer: string`, `historyIndex: number`, `history: string[]` (loaded from `historyPath` on mount, appended on submit).

Key bindings:
| Input | Action |
|---|---|
| Printable chars | Append to buffer |
| Backspace | Delete last char |
| ↑ / ↓ | Cycle history |
| Tab | Call `commandRegistry.getCompletions()`, insert first match |
| Alt+Enter | Insert `\n` into buffer |
| Enter | Emit `'submit'` on store, save to history |
| Ctrl+C | `console.confirm('Do you want to quit?')` → `process.exit(0)` or continue |

Default text (interrupt-restore) comes from `store.promptDefault`.

---

### CommandRegistry & Command Base

```typescript
abstract class Command {
  constructor(protected app: IApplication) {}
  abstract get name(): string
  abstract get description(): string
  abstract execute(args: string): Promise<void>
  async getCompletions(text: string): Promise<string[]> { return [] }
}
```

`CommandRegistry` extends `Service`. On `boot()` initialises `_commands: Map<string, Command>`.

- `register(command)` — add to map
- `handle(input)` — parse `/name args`, look up, call `execute(args)`. Unknown command → `console.printError('Unknown command: /name')`
- `getCompletions(text)` — returns `[name, description][]` for prefix matching on command names; delegates to `command.getCompletions(args)` when a space is present

**`/exit`** — `process.exit(0)`

**`/help`** — iterates commands, prints name + description table via `console.print()` with `▌▌` border style

---

### InteractionService

Wraps `Console` service methods for agent/service use:

- `confirm(message, default?)` → `console.confirm(...)` → `Promise<boolean>`
- `select(message, choices[], default?)` → `console.select(...)` → `Promise<string>`
- `inputText(message, default?)` → sets a text-input modal state → `Promise<string>`

Throws `InputCancelledError` on Esc/Ctrl+C (matching Python behaviour).

---

### StreamRenderingService (Stub)

Implements the same interface as the Python `StreamRenderingService`. All methods are no-ops or log a placeholder. Will be fully implemented when the agent domain is migrated.

```typescript
class StreamRenderingService extends Service {
  async handleMessage(_chunk: unknown, _agentName: string): Promise<void> {}
  async startSpinner(_message?: string): Promise<void> {}
  async stopSpinner(): Promise<void> {}
  async endStream(): Promise<void> {}
  setDisplayMode(_mode: string): void {}
}
```

---

### Ink Components

**`<RuneSpinner>`** — `useEffect` with `setInterval` at 40ms. Computes animated chars via `(frame + i) * 31 % runes.length` (same deterministic seed as Python). Rune set: `"0123456789abcdefABCDEF~!@#$%^&*()+=_"`. Colours cycle through `primary`, `secondary`, `text`.

**`<Menu>`** — `useInput` for arrow / hjkl / Enter / Esc. Two modes:
- `select` — vertical scrolling list (window of 5), single choice
- `confirm` — horizontal Yes/No, left/right navigation

On confirm: calls `props.onConfirm(value)` → `modal.resolve(value)` → promise resolves in `Console` service.

**`<ByteDisplay>`** — Renders each line prefixed with `▌▌` in `primary`/`secondary` theme colours using `<Text>`.

**`<MarkdownStream>`** — Receives `live: LiveContent` from store. Runs `marked` + `marked-terminal` on full accumulated content each update (same sliding-window approach as Python). Pre-processes `<agent_plan>` and `<operation_block>` tags before markdown parsing — identical regex replacements to Python's `_preprocess_tags`. Uses `<ByteDisplay>` for ` ```byte ` blocks.

**`theme.ts`** — Maps named colours (`primary`, `secondary`, `muted`, `error`, `text`, `active_border`, `inactive_border`, `danger`) to hex values. All components import from here.

---

### CLIServiceProvider

```typescript
class CLIServiceProvider extends ServiceProvider {
  services() {
    return [
      Console,
      PromptService,
      CommandRegistry,
      InteractionService,
      StreamRenderingService,
    ]
  }

  async boot() {
    const registry = this.app.make(CommandRegistry)
    registry.register(new ExitCommand(this.app))
    registry.register(new HelpCommand(this.app))

    const eventBus = this.app.make(EventBus)
    eventBus.on(EventType.POST_BOOT, this.bootMessages.bind(this))
  }

  async bootMessages(payload: Payload): Promise<Payload> {
    // Logo (diagonal gradient), version, root path — port of Python boot_messages
    ...
    return payload
  }
}
```

---

### Entry Point (`main.ts`)

```typescript
import { render } from 'ink'
import React from 'react'
import { Application } from './foundation/index.ts'
import { FoundationServiceProvider } from './foundation/index.ts'
import { CLIServiceProvider, Console, App } from './cli/index.ts'

const app = Application.configure(process.cwd(), [
  FoundationServiceProvider,
  CLIServiceProvider,
]).create()

await app.boot()

const consoleService = app.make<Console>('console')
const promptService = app.make<PromptService>(PromptService)
const cachePath = app.make<string>('path.cache')
render(React.createElement(App, { console: consoleService, promptService, cachePath }))
```

`node/package.json` bin field:
```json
"bin": { "byte": "./src/main.ts" }
```

`bun link` inside `node/` wires `byte` to `$PATH`. `flake.nix` update (point Nix package at Node entry) is noted as a plan step but out of scope for this design.

---

### Testing

Unit tests cover pure logic only. Ink components are not unit tested (awkward in `bun test`) — verified manually at boot.

| File | What it tests |
|---|---|
| `console-store.test.ts` | State transitions, EventEmitter notifications, `setState` merging |
| `command-registry.test.ts` | Register, handle, completions, unknown command error |
| `interaction-service.test.ts` | confirm/select resolve correctly via mock Console |
| `prompt-service.test.ts` | Submit routing: slash → registry, plain → stub, empty → no-op |

---

## Circular Import Note

`Console` service token is registered as string key `'console'` in the container (same pattern as `'event-bus'`). Components receive the `Console` service as a prop from `main.ts` — no DI container imports inside `components/`.

---

## Out of Scope

- Agent execution (stubbed)
- `flake.nix` Nix package update
- Remaining slash commands (files, memory, git, etc.)
- `SubprocessService` (`!` shell command prefix)
- `@`-command syntax
