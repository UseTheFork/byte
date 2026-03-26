# Design: Foundation & Support Domain — Python to Node/TS Migration

**Date:** 2026-03-26
**Branch:** dev-v3-node
**Scope:** `foundation` and `support` domains only. Python code is preserved in `src/` and serves as the reference implementation. The Node/TS build lives in parallel under `node/`.

---

## Overview

Migrate the `foundation` and `support` domains of the byte CLI application from Python to TypeScript, running under Bun. The two codebases coexist in the same repository — Python in `src/`, Node/TS in `node/` — with no shared runtime or symlinks. The Python side is the reference spec for behavior.

Architecture mirrors the Python implementation closely: same service provider pattern, same DI container lifecycle, same two-phase boot (register → boot), same domain boundaries enforced by barrel `index.ts` files.

---

## Tooling

| Concern | Choice |
|---|---|
| Runtime | Bun (native TS execution, no build step) |
| Tests | `bun test` (built-in, no extra dependencies) |
| TypeScript | Strict mode, `moduleResolution: bundler`, `target: ESNext` |
| Entry point | `node/src/index.ts` |
| YAML parsing | `js-yaml` (Bun does not include a native YAML parser) |
| Git root detection | `simple-git` |

---

## Repository Layout

```
node/
  src/
    foundation/
      index.ts                  ← public API barrel
      application.ts
      application-builder.ts
      container.ts
      event-bus.ts
      task-manager.ts
      kernel.ts
      exceptions.ts
      bootstrap/
        index.ts
        register-providers.ts
        load-configuration.ts
        load-environment-variables.ts
        load-console-args.ts
        prepare-environment.ts
        handle-exceptions.ts
        set-context.ts
      console/
        index.ts
        console.ts
        kernel.ts
    support/
      index.ts                  ← public API barrel
      service.ts
      service-provider.ts
      array-store.ts
      boundary.ts
      boundary-extractor.ts
      str.ts
      yaml.ts
      concerns/                 ← renamed from mixins
        index.ts
        bootable.ts
        eventable.ts
        configurable.ts
        conditionable.ts
      utils/
        index.ts
        dump.ts
        slugify.ts
        value.ts
        extract-content-from-message.ts
        extract-json-from-message.ts
        get-language-from-filename.ts
        get-last-ai-message.ts
        get-last-message.ts
        list-to-multiline-text.ts
        parse-partial-json.ts
    index.ts                    ← re-exports all domain public APIs
  tests/
    foundation/
    support/
  package.json
  tsconfig.json
  bunfig.toml
```

Python source remains untouched in `src/byte/`.

---

## `support` Domain

The support domain has no dependencies on other byte domains. It provides the base abstractions all other domains build on.

### `ArrayStore<T = unknown>`

Direct port of `support/concerns/array_store.py`. Fluent key-value store.

Methods: `add(key, value)`, `get(key, default?)`, `all()`, `merge(...dicts)`, `remove(key)`, `set(data)`, `isEmpty()`, `isNotEmpty()`.

### `Str`

Static utility class. All methods ported directly:
- `contains(haystack, needles, ignoreCase?)`
- `snakeCase(value)`
- `slugify(text, separator?)`
- `isPattern(pattern, value, ignoreCase?)`
- `classToString(abstract)` — returns `constructor.name` (TS has no `__module__`; DI key resolution handled separately in Container via Symbol tokens)
- `classToSnakeCase(abstract)`
- `substrCount(haystack, needle, offset?, length?)`
- `beforeLast(subject, search)`
- `afterLast(subject, search)`
- `parseCallback(callback, default?)`

### `BoundaryType` and `Boundary`

`BoundaryType` is defined as an `as const` object with a corresponding exported union type — more idiomatic TS than an enum, better IDE support and tree-shaking.

```ts
export const BoundaryType = {
  ROLE: 'role',
  TASK: 'task',
  // ...all values from Python enum
} as const

export type BoundaryType = typeof BoundaryType[keyof typeof BoundaryType]
```

`Boundary` is a class with static methods: `open(type, meta?, format?)`, `close(type, format?)`, `notice(content, format?)`, `critical(content, format?)`, `important(content, format?)`, `warning(content, format?)`, `comment(content)`. Identical signatures and behavior to Python.

### `BoundaryExtractor`

Static class. Methods: `extract(text, boundaryType)` and `extractAll(text, boundaryType)`. Regex-based, direct port.

### `Yaml`

Static class using `js-yaml`. Methods: `load(path)` and `loadAsDict(path)`. Uses `Bun.file()` for reading.

### `concerns/` (Mixins)

Python uses MRO-based automatic mixin boot discovery (`_boot_mixins` scans `__mro__` for `boot_<classname>` methods). TypeScript has no MRO. The replacement:

- **`Bootable`** — abstract base class. Protected `app` property. `ensureBooted()` calls `bootConcerns()` then `boot()`. `bootConcerns()` is a protected method that subclasses can override to call mixin boot methods explicitly. No magic scanning.
- **`Eventable`** — interface with a single method `emit(payload): Promise<Payload>`. Not a class — avoids single-inheritance conflict. `Service` extends `Bootable` and implements `Eventable` directly in its body (the implementation resolves `EventBus` from `this.app`, which `Bootable` already provides).
- **`Configurable`** — interface + default implementation mixin (a function that returns a class). Adds `config(): ArrayStore` and `bootConfigurable()`.
- **`Conditionable`** — interface + default implementation mixin, ported from Python equivalent.

`Service` composes these by extending `Bootable` (the one abstract base class) and implementing the `Eventable`, `Configurable`, and `Conditionable` interfaces directly.

### `Service`

Abstract class. Extends `Bootable`, implements `Eventable`, `Configurable`, and `Conditionable` interfaces.

Methods:
- `validate(): Promise<boolean>` — override in concrete classes
- `handle(...args): Promise<unknown>` — override in concrete classes
- `run(...args): Promise<unknown>` — validates then handles (replaces Python `__call__`)

### `ServiceProvider`

Abstract class. Constructor receives `app: IApplication` (interface, not concrete `Application` — avoids circular import).

Methods:
- `services(): Array<typeof Service>` — returns `[]` by default
- `commands(): Array<typeof Command>` — returns `[]` by default
- `registerServices()` — registers each service as singleton
- `registerCommands()` — registers each command
- `register()` — phase 1 binding (override in subclasses)
- `boot(): Promise<void>` — phase 2 init (override in subclasses)
- `shutdown(app: IApplication): Promise<void>` — cleanup (override in subclasses)

---

## `foundation` Domain

Depends on `support`. Provides the application lifecycle, DI container, event system, and bootstrap sequence.

### DI Key Strategy

Python uses `f"{cls.__module__}.{cls.__qualname__}"` as the container key. TypeScript has no reliable module path at runtime. Solution:

Each injectable class exposes a static `token: symbol` property:

```ts
class MyService {
  static token = Symbol('MyService')
}
```

`Container.make(MyService)` uses `MyService.token` as the lookup key. String keys (`"app"`, `"env"`, `"path"`, etc.) continue to work as-is. `Str.classToString` returns `constructor.name` for display only; DI resolution always goes through the token.

### `Container`

Three internal maps: `_singletons: Map<symbol|string, Factory>`, `_instances: Map<symbol|string, unknown>`, `_transients: Map<symbol|string, Factory>`.

Methods: `bind(cls, factory?)`, `singleton(cls, factory?)`, `instance(abstract, value)`, `make(abstract)`, `build(cls, ...kwargs)`, `flush()`, `bound(abstract)`.

`__getitem__` / `__setitem__` equivalents: `get(key)` / `set(key, value)` — or implement via `Proxy` if desired. Decision deferred to implementation — keep it simple first.

### `Application`

Extends `Container`. Implements `IApplication` interface.

Properties: `basePath`, `gitRootPath`, `_booted`, `_hasBeenBootstrapped`, `_bootingCallbacks`, `_bootedCallbacks`.

Path helpers: `rootPath(path?)`, `appPath(path?)`, `basePath(path?)`, `configPath(path?)`, `cachePath(path?)`, `conventionsPath(path?)`, `sessionContextPath(path?)`, `joinPaths(base, path?)`.

Lifecycle: `configure(basePath?, providers?)` static factory → returns `ApplicationBuilder`. `boot()` iterates `RegisterProviders._merge` and calls `bootProvider()`. `run()` starts the interactive prompt loop. `terminate()`.

Environment helpers: `isDevelopment()`, `isProduction()`, `runningUnitTests()`, `detectEnvironment(callback)`.

Git root: detected at construction using `simple-git` with `search_parent_directories` equivalent.

### `ApplicationBuilder`

Fluent builder. `withKernels()`, `withProviders(providers?)`, `create(): Application`.

### `EventBus`

`EventType` as `as const` + union — all current Python event types ported.

`Payload` class wraps `ArrayStore`. Constructor: `(eventType, data?, timestamp?)`. Methods: `get(key, default?)`, `set(key, value)`, `update(updates)`.

`EventBus` class: `on(eventName, callback)`, `async emit(payload): Promise<Payload>`. Chains listeners sequentially, supports async. Errors logged via `app["log"]`.

### `TaskManager`

Extends `Bootable`. Manages named background tasks using `Promise` references and `AbortController` for cancellation where applicable.

Methods: `startTask(name, promise)`, `stopTask(name)`, `dispatchTask(promise)`, `shutdown(): Promise<void>`.

### `Kernel`

Orchestrates bootstrap. `bootstrappers()` returns ordered array of bootstrapper classes. `bootstrap()` calls `app.bootstrapWith(bootstrappers())`. `handle(input): Promise<number>` calls bootstrap → `app.boot()` → `app.run()`. `terminate()`.

### Bootstrap Sequence

Each bootstrapper is a class with `bootstrap(app: Application): void | Promise<void>`:

1. `LoadEnvironmentVariables` — uses Bun's built-in `process.env` + `.env` file loading
2. `LoadConsoleArgs` — reads `process.argv`
3. `PrepareEnvironment` — binds `env` in container
4. `LoadConfiguration` — loads `.byte/` YAML config files
5. `SetContext` — binds session context path
6. `HandleExceptions` — sets `process.on('uncaughtException', ...)` handler
7. `RegisterProviders` — merges and registers all service providers

### `FoundationServiceProvider`

Registers `EventBus`, `TaskManager`, `Console` as singletons.

### Circular Import Resolution

`Application` and `ServiceProvider` mutually reference each other. Resolved with a shared `IApplication` interface defined in `support/`:

- `ServiceProvider` depends on `IApplication` (interface)
- `Application` implements `IApplication`
- No runtime circular dependency

---

## Testing Strategy

Tests live in `node/tests/` mirroring the source structure. Use `bun test`.

- `support/` tests: unit tests for each utility class — `ArrayStore`, `Str`, `Boundary`, `BoundaryExtractor`, `Yaml`
- `foundation/` tests: `Container` resolution, `Application` lifecycle, `EventBus` emit/listen, `TaskManager` dispatch/shutdown
- No mocking of the container itself — test real resolution as the Python test suite does

---

## What Is NOT in Scope

This spec covers `foundation` and `support` only. The following domains are explicitly deferred:

`config`, `cli`, `agent`, `analytics`, `files`, `git`, `knowledge`, `lint`, `llm`, `lsp`, `memory`, `mcp`, `parsing`, `presets`, `system`, `tools`, `web`, `development`, `conventions`, `code_operations`, `workflow`, `clipboard`, `logging`

Each will follow its own spec → plan → implementation cycle.
