# Config Domain Node/TS Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the byte config domain from Python (Pydantic) to TypeScript (Zod), giving the Node runtime a typed, default-filled `ByteConfig` object from `app.make<ByteConfig>('config')`.

**Architecture:** A `node/src/config/` package holds all Zod schemas and the `ByteConfigException`. The existing `LoadConfiguration` bootstrapper (currently a stub) is updated to parse and validate the loaded YAML with Zod, bind the typed result to the DI container, and call `detectEnvironment`. No service provider is needed — config is bootstrapped, not registered as a service.

**Tech Stack:** Bun, TypeScript strict + `verbatimModuleSyntax`, Zod (new dependency), `js-yaml` (already present via `Yaml` utility).

---

## File Map

**New files to create:**

| File | Purpose |
|---|---|
| `node/src/config/schemas.ts` | All Zod schemas + inferred TypeScript types |
| `node/src/config/exceptions.ts` | `ByteConfigException extends ByteException` |
| `node/src/config/index.ts` | Barrel — re-exports schemas, types, exception |
| `node/tests/config/schemas.test.ts` | Schema defaults + validation tests |
| `node/tests/config/load-configuration.test.ts` | LoadConfiguration bootstrapper tests |

**Files to modify:**

| File | Change |
|---|---|
| `node/package.json` | Add `zod` runtime dependency |
| `node/src/foundation/bootstrap/load-configuration.ts` | Replace stub with Zod validation |

---

## Task 1: Add Zod Dependency

**Files:**
- Modify: `node/package.json`

- [ ] **Step 1: Install zod**

```bash
cd /path/to/repo/node && bun add zod
```

Expected: `package.json` now contains `"zod": "^3.x.x"` in `dependencies`.

- [ ] **Step 2: Run existing tests to verify no regressions**

```bash
cd node && bun test
```

Expected: All tests pass (same count as before).

- [ ] **Step 3: Commit**

```bash
cd node
git add package.json bun.lock
git commit -m "feat(config): add zod dependency"
```

---

## Task 2: Config Schemas (TDD)

**Files:**
- Create: `node/tests/config/schemas.test.ts`
- Create: `node/src/config/schemas.ts`

- [ ] **Step 1: Write the failing test**

Create `node/tests/config/schemas.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { ByteConfigSchema } from '../../src/config/schemas.ts'

describe('ByteConfigSchema', () => {
  it('parses empty object to full defaults', () => {
    const config = ByteConfigSchema.parse({})
    expect(config.app.env).toBe('production')
    expect(config.app.debug).toBe(false)
    expect(config.cli.ui_theme).toBe('mocha')
    expect(config.cli.syntax_theme).toBe('monokai')
    expect(config.llm.main_model.model).toBe('')
    expect(config.llm.weak_model.model).toBe('')
    expect(config.git.max_description_length).toBe(72)
    expect(config.git.enable_scopes).toBe(false)
    expect(config.git.enable_breaking_changes).toBe(true)
    expect(config.git.scopes).toContain('cli')
    expect(config.lint.enable).toBe(false)
    expect(config.lint.commands).toEqual([])
    expect(config.files.watch.enable).toBe(false)
    expect(config.files.ignore).toContain('node_modules')
    expect(config.edit_format.enable_shell_commands).toBe(false)
    expect(config.edit_format.mask_message_count).toBe(1)
    expect(config.presets).toEqual([])
    expect(config.boot.read_only_files).toEqual([])
  })

  it('merges partial llm config over defaults', () => {
    const config = ByteConfigSchema.parse({
      llm: { main_model: { model: 'claude-sonnet-4-5' } },
    })
    expect(config.llm.main_model.model).toBe('claude-sonnet-4-5')
    expect(config.llm.weak_model.model).toBe('')  // default preserved
    expect(config.llm.main_model.provider).toBe('')  // default preserved
  })

  it('throws on invalid ui_theme enum value', () => {
    expect(() => ByteConfigSchema.parse({ cli: { ui_theme: 'invalid' } })).toThrow()
  })

  it('throws on invalid syntax_theme enum value', () => {
    expect(() => ByteConfigSchema.parse({ cli: { syntax_theme: 'bad-theme' } })).toThrow()
  })

  it('parses real-world config structure correctly', () => {
    const config = ByteConfigSchema.parse({
      llm: {
        main_model: { model: 'claude-sonnet-4-5' },
        weak_model: { model: 'claude-haiku-4-5' },
      },
      lint: {
        enable: true,
        commands: [{ command: ['ruff', 'check', '--fix'], languages: ['python'] }],
      },
      presets: [{ id: 'base', load_on_boot: false, conventions: ['CODE_PATTERNS.md'] }],
      git: { enable_scopes: true, max_description_length: 80 },
    })
    expect(config.llm.main_model.model).toBe('claude-sonnet-4-5')
    expect(config.llm.weak_model.model).toBe('claude-haiku-4-5')
    expect(config.lint.enable).toBe(true)
    expect(config.lint.commands).toHaveLength(1)
    expect(config.lint.commands[0]?.command).toEqual(['ruff', 'check', '--fix'])
    expect(config.presets[0]?.id).toBe('base')
    expect(config.presets[0]?.conventions).toEqual(['CODE_PATTERNS.md'])
    expect(config.git.enable_scopes).toBe(true)
    expect(config.git.max_description_length).toBe(80)
    expect(config.git.enable_breaking_changes).toBe(true)  // default preserved
  })

  it('unknown top-level keys are stripped silently', () => {
    // lsp, mcp, web, system are not in the schema — Zod strips them
    const config = ByteConfigSchema.parse({ lsp: { enable: true }, web: { enable: true } })
    expect((config as Record<string, unknown>)['lsp']).toBeUndefined()
    expect((config as Record<string, unknown>)['web']).toBeUndefined()
    // No throw — graceful handling of not-yet-migrated sections
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd node && bun test tests/config/schemas.test.ts
```

Expected: Error — cannot find module `../../src/config/schemas.ts`

- [ ] **Step 3: Implement schemas.ts**

Create `node/src/config/schemas.ts`:

```typescript
import { z } from 'zod'

const AppConfigSchema = z.object({
  env:     z.string().default('production'),
  debug:   z.boolean().default(false),
  version: z.string().default('0.0.0'),
})

const BootConfigSchema = z.object({
  read_only_files: z.array(z.string()).default([]),
  editable_files:  z.array(z.string()).default([]),
})

const CLIConfigSchema = z.object({
  ui_theme:     z.enum(['mocha', 'macchiato', 'latte', 'frappe']).default('mocha'),
  syntax_theme: z.enum(['github-dark', 'bw', 'sas', 'staroffice', 'xcode', 'monokai', 'lightbulb', 'rrt']).default('monokai'),
})

const LLMModelConfigSchema = z.object({
  provider:     z.string().default(''),
  model:        z.string().default(''),
  extra_params: z.record(z.unknown()).default({}),
})

const LLMConfigSchema = z.object({
  main_model: LLMModelConfigSchema.default({}),
  weak_model: LLMModelConfigSchema.default({}),
})

const GitConfigSchema = z.object({
  enable_scopes:           z.boolean().default(false),
  enable_breaking_changes: z.boolean().default(true),
  enable_body:             z.boolean().default(true),
  scopes:                  z.array(z.string()).default(['api', 'auth', 'cli', 'config', 'core', 'db', 'deps', 'docs', 'test', 'ui']),
  description_guidelines:  z.array(z.string()).default([]),
  max_description_length:  z.number().int().default(72),
})

const WatchConfigSchema = z.object({
  enable: z.boolean().default(false),
})

const FilesConfigSchema = z.object({
  watch: WatchConfigSchema.default({}),
  ignore: z.array(z.string()).default([
    '.byte/cache', '.ruff_cache', '.idea', '.venv', '.env',
    '.git', '.pytest_cache', '__pycache__', 'node_modules', 'dist',
  ]),
})

const LintCommandSchema = z.object({
  command:   z.array(z.string()),
  languages: z.array(z.string()),
})

const LintConfigSchema = z.object({
  enable:   z.boolean().default(false),
  commands: z.array(LintCommandSchema).default([]),
})

const PresetsConfigSchema = z.object({
  id:              z.string(),
  read_only_files: z.array(z.string()).default([]),
  editable_files:  z.array(z.string()).default([]),
  conventions:     z.array(z.string()).default([]),
  prompt:          z.string().nullable().default(null),
  load_on_boot:    z.boolean().default(false),
})

const EditFormatConfigSchema = z.object({
  enable_shell_commands: z.boolean().default(false),
  mask_message_count:    z.number().int().default(1),
})

export const ByteConfigSchema = z.object({
  version:     z.string().default('0.0.0'),
  app:         AppConfigSchema.default({}),
  boot:        BootConfigSchema.default({}),
  cli:         CLIConfigSchema.default({}),
  edit_format: EditFormatConfigSchema.default({}),
  files:       FilesConfigSchema.default({}),
  git:         GitConfigSchema.default({}),
  lint:        LintConfigSchema.default({}),
  llm:         LLMConfigSchema.default({}),
  presets:     z.array(PresetsConfigSchema).default([]),
})

export type ByteConfig       = z.infer<typeof ByteConfigSchema>
export type AppConfig        = z.infer<typeof AppConfigSchema>
export type BootConfig       = z.infer<typeof BootConfigSchema>
export type CLIConfig        = z.infer<typeof CLIConfigSchema>
export type LLMConfig        = z.infer<typeof LLMConfigSchema>
export type LLMModelConfig   = z.infer<typeof LLMModelConfigSchema>
export type GitConfig        = z.infer<typeof GitConfigSchema>
export type FilesConfig      = z.infer<typeof FilesConfigSchema>
export type LintConfig       = z.infer<typeof LintConfigSchema>
export type LintCommand      = z.infer<typeof LintCommandSchema>
export type PresetsConfig    = z.infer<typeof PresetsConfigSchema>
export type EditFormatConfig = z.infer<typeof EditFormatConfigSchema>
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd node && bun test tests/config/schemas.test.ts
```

Expected: 6 tests pass.

- [ ] **Step 5: Commit**

```bash
cd node
git add src/config/schemas.ts tests/config/schemas.test.ts
git commit -m "feat(config): add Zod schemas for ByteConfig and sub-domains"
```

---

## Task 3: ByteConfigException and Barrel

**Files:**
- Create: `node/src/config/exceptions.ts`
- Create: `node/src/config/index.ts`

No unit tests — `ByteConfigException` is tested implicitly in Task 4 via `LoadConfiguration` tests.

- [ ] **Step 1: Create exceptions.ts**

Create `node/src/config/exceptions.ts`:

```typescript
import { ByteException } from '../foundation/exceptions.ts'

export class ByteConfigException extends ByteException {
  constructor(message: string) {
    super(message)
    this.name = 'ByteConfigException'
  }
}
```

- [ ] **Step 2: Create index.ts barrel**

Create `node/src/config/index.ts`:

```typescript
export { ByteConfigSchema } from './schemas.ts'
export type {
  ByteConfig,
  AppConfig,
  BootConfig,
  CLIConfig,
  LLMConfig,
  LLMModelConfig,
  GitConfig,
  FilesConfig,
  LintConfig,
  LintCommand,
  PresetsConfig,
  EditFormatConfig,
} from './schemas.ts'
export { ByteConfigException } from './exceptions.ts'
```

- [ ] **Step 3: Run all tests to verify no regressions**

```bash
cd node && bun test
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
cd node
git add src/config/exceptions.ts src/config/index.ts
git commit -m "feat(config): add ByteConfigException and config barrel"
```

---

## Task 4: Update LoadConfiguration Bootstrapper (TDD)

**Files:**
- Create: `node/tests/config/load-configuration.test.ts`
- Modify: `node/src/foundation/bootstrap/load-configuration.ts`

- [ ] **Step 1: Write the failing test**

Create `node/tests/config/load-configuration.test.ts`:

```typescript
import { describe, it, expect } from 'bun:test'
import { mkdtempSync, writeFileSync } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import { LoadConfiguration } from '../../src/foundation/bootstrap/load-configuration.ts'
import { ByteConfigException } from '../../src/config/exceptions.ts'
import type { ByteConfig } from '../../src/config/schemas.ts'

function makeTempConfigDir(yamlContent: string): string {
  const dir = mkdtempSync(join(tmpdir(), 'byte-config-test-'))
  writeFileSync(join(dir, 'config.yaml'), yamlContent)
  return dir
}

function makeApp(configDir: string) {
  const state: { key: string; value: ByteConfig | undefined; env: string } = {
    key: '',
    value: undefined,
    env: '',
  }
  const app = {
    configPath: () => configDir,
    instance: (key: string, value: unknown) => { state.key = key; state.value = value as ByteConfig },
    detectEnvironment: (fn: () => string) => { state.env = fn() },
  }
  return { app, state }
}

describe('LoadConfiguration', () => {
  it('binds typed ByteConfig to app under "config" key', () => {
    const dir = makeTempConfigDir(
      'llm:\n  main_model:\n    model: claude-sonnet-4-5\n'
    )
    const { app, state } = makeApp(dir)
    new LoadConfiguration().bootstrap(app as never)
    expect(state.key).toBe('config')
    expect(state.value?.llm.main_model.model).toBe('claude-sonnet-4-5')
    expect(state.value?.llm.weak_model.model).toBe('')
  })

  it('boots with full defaults when config.yaml is absent', () => {
    const dir = mkdtempSync(join(tmpdir(), 'byte-config-test-'))
    // No config.yaml written — Yaml.loadAsDict returns {}
    const { app, state } = makeApp(dir)
    new LoadConfiguration().bootstrap(app as never)
    expect(state.value?.cli.ui_theme).toBe('mocha')
    expect(state.value?.git.max_description_length).toBe(72)
    expect(state.value?.presets).toEqual([])
  })

  it('throws ByteConfigException on invalid config', () => {
    const dir = makeTempConfigDir('cli:\n  ui_theme: not-a-valid-theme\n')
    const { app } = makeApp(dir)
    expect(() => new LoadConfiguration().bootstrap(app as never))
      .toThrow(ByteConfigException)
  })

  it('calls detectEnvironment with config.app.env', () => {
    const dir = makeTempConfigDir('app:\n  env: testing\n')
    const { app, state } = makeApp(dir)
    new LoadConfiguration().bootstrap(app as never)
    expect(state.env).toBe('testing')
  })

  it('uses "production" env by default', () => {
    const dir = mkdtempSync(join(tmpdir(), 'byte-config-test-'))
    const { app, state } = makeApp(dir)
    new LoadConfiguration().bootstrap(app as never)
    expect(state.env).toBe('production')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd node && bun test tests/config/load-configuration.test.ts
```

Expected: 5 tests fail — current implementation does not validate with Zod or call `detectEnvironment`.

- [ ] **Step 3: Implement the updated LoadConfiguration**

Replace the entire contents of `node/src/foundation/bootstrap/load-configuration.ts`:

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'
import { Yaml } from '../../support/yaml.ts'
import { ByteConfigSchema } from '../../config/schemas.ts'
import { ByteConfigException } from '../../config/exceptions.ts'
import path from 'path'

export class LoadConfiguration implements Bootstrapper {
  bootstrap(app: Application): void {
    const raw = Yaml.loadAsDict(path.join(app.configPath(), 'config.yaml'))

    const result = ByteConfigSchema.safeParse(raw)
    if (!result.success) {
      throw new ByteConfigException(
        `Invalid configuration: ${result.error.message}`
      )
    }

    app.instance('config', result.data)
    app.detectEnvironment(() => result.data.app.env)
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd node && bun test tests/config/load-configuration.test.ts
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
git add src/foundation/bootstrap/load-configuration.ts tests/config/load-configuration.test.ts
git commit -m "feat(config): validate and type config via Zod in LoadConfiguration"
```
