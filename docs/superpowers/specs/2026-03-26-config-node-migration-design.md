# Design: Config Domain — Python to Node/TS Migration

**Date:** 2026-03-26
**Branch:** dev-v3-node
**Scope:** `config` domain — Zod schemas for 6 sub-domain configs, `ByteConfigException`, updated `LoadConfiguration` bootstrapper. Migrations and `Repository` are out of scope. Python source is preserved and serves as the reference implementation.

---

## Overview

Port the config layer of the byte CLI from Python (Pydantic models) to TypeScript (Zod schemas), running under Bun. The Node binary currently loads `config.yaml` as a raw untyped dict. After this migration, `app.make<ByteConfig>('config')` returns a fully-typed, default-filled, Zod-validated config object.

There is no `ConfigServiceProvider` — matching the Python pattern where config is bootstrapped via `LoadConfiguration`, not registered as a service.

---

## Tooling Additions

| Concern | Choice |
|---|---|
| Schema validation + types | `zod` |

---

## Repository Layout

```
node/src/config/
  schemas.ts           ← Zod schemas for 6 sub-domains + ByteConfigSchema + inferred types
  exceptions.ts        ← ByteConfigException
  index.ts             ← barrel

node/src/foundation/bootstrap/load-configuration.ts   ← updated (was a stub)

node/tests/config/
  schemas.test.ts      ← defaults + validation + LoadConfiguration integration tests
```

**Modified files:**
- `node/package.json` — add `zod`
- `node/src/foundation/bootstrap/load-configuration.ts` — replace stub with Zod-validated bootstrap

---

## Architecture

### Schemas (`schemas.ts`)

All schemas use Zod's `.default()` so that `ByteConfigSchema.parse({})` produces a fully-populated typed object. Unknown YAML keys (e.g., `lsp`, `mcp`, `web`, `system`) are silently stripped by Zod — no error, no breakage when those sections exist in the user's config.yaml.

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
  watch:  WatchConfigSchema.default({}),
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

// Inferred types — consumers import these, not the schema objects
export type ByteConfig        = z.infer<typeof ByteConfigSchema>
export type AppConfig         = z.infer<typeof AppConfigSchema>
export type BootConfig        = z.infer<typeof BootConfigSchema>
export type CLIConfig         = z.infer<typeof CLIConfigSchema>
export type LLMConfig         = z.infer<typeof LLMConfigSchema>
export type LLMModelConfig    = z.infer<typeof LLMModelConfigSchema>
export type GitConfig         = z.infer<typeof GitConfigSchema>
export type FilesConfig       = z.infer<typeof FilesConfigSchema>
export type LintConfig        = z.infer<typeof LintConfigSchema>
export type LintCommand       = z.infer<typeof LintCommandSchema>
export type PresetsConfig     = z.infer<typeof PresetsConfigSchema>
export type EditFormatConfig  = z.infer<typeof EditFormatConfigSchema>
```

---

### Exception (`exceptions.ts`)

```typescript
import { ByteException } from '../foundation/exceptions.ts'

export class ByteConfigException extends ByteException {
  constructor(message: string) {
    super(message)
    this.name = 'ByteConfigException'
  }
}
```

---

### Updated `LoadConfiguration` Bootstrapper

Replaces the existing stub. On validation failure, surfaces Zod's structured error message via `ByteConfigException` rather than crashing with a raw Zod error.

```typescript
import type { Bootstrapper } from './bootstrapper.ts'
import type { Application } from '../application.ts'
import { Yaml } from '../../support/yaml.ts'
import { ByteConfigSchema } from '../../config/schemas.ts'
import { ByteConfigException } from '../../config/exceptions.ts'
import path from 'path'

export class LoadConfiguration implements Bootstrapper {
  bootstrap(app: Application): void {
    const configPath = app.configPath()
    const raw = Yaml.loadAsDict(path.join(configPath, 'config.yaml'))

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

`Yaml.loadAsDict()` returns `{}` when `config.yaml` is absent, so the CLI boots with full defaults when no config file exists.

---

### Barrel (`index.ts`)

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

---

### Testing

```typescript
// tests/config/schemas.test.ts
describe('ByteConfigSchema', () => {
  it('parses empty object to full defaults')
  // expect: llm.main_model.model === '', git.max_description_length === 72,
  //         lint.enable === false, files.ignore contains 'node_modules',
  //         cli.ui_theme === 'mocha', presets === []

  it('merges partial config over defaults')
  // input: { llm: { main_model: { model: 'claude-sonnet-4-5' } } }
  // expect: llm.main_model.model === 'claude-sonnet-4-5', weak_model.model === ''

  it('throws on invalid enum value')
  // input: { cli: { ui_theme: 'invalid' } }
  // expect: throws ZodError

  it('parses real-world config.yaml structure correctly')
  // input: representative subset of the real config (llm + lint + presets)
  // expect: all fields populated as expected
})

describe('LoadConfiguration', () => {
  it('binds typed config to app')
  // mock app with instance() and detectEnvironment() mocks
  // expect: app.instance called with 'config' and a valid ByteConfig

  it('throws ByteConfigException on invalid config')
  // mock Yaml.loadAsDict to return { cli: { ui_theme: 'bad' } }
  // expect: throws ByteConfigException

  it('boots with defaults when config.yaml absent')
  // mock Yaml.loadAsDict to return {}
  // expect: app.instance called with 'config' containing full defaults
})
```

---

## Out of Scope

- Config migrations (`Migrator`, `BaseMigration`)
- `Repository` (typed flat-key getters) — unnecessary with Zod inferred types
- Remaining 5 sub-domains: `lsp`, `mcp`, `web`, `system` schemas
- `Yaml.save()` (needed by migrations only)
- Merging CLI args into `boot` config (deferred to agent domain migration)
