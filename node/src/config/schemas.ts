import { z } from 'zod'

const AppConfigSchema = z.object({
  env:     z.string().default('production'),
  debug:   z.boolean().default(false),
  version: z.string().default('0.0.0'),
}).strict()

const BootConfigSchema = z.object({
  read_only_files: z.array(z.string()).default([]),
  editable_files:  z.array(z.string()).default([]),
}).strict()

const CLIConfigSchema = z.object({
  ui_theme:     z.enum(['mocha', 'macchiato', 'latte', 'frappe']).default('mocha'),
  syntax_theme: z.enum(['github-dark', 'bw', 'sas', 'staroffice', 'xcode', 'monokai', 'lightbulb', 'rrt']).default('monokai'),
}).strict()

const LLMModelConfigSchema = z.object({
  provider:     z.string().default(''),
  model:        z.string().default(''),
  extra_params: z.record(z.string(), z.unknown()).default({}),
}).strict()

const LLMConfigSchema = z.object({
  main_model: LLMModelConfigSchema.optional(),
  weak_model: LLMModelConfigSchema.optional(),
}).strict().transform((data) => ({
  main_model: LLMModelConfigSchema.parse(data.main_model || {}),
  weak_model: LLMModelConfigSchema.parse(data.weak_model || {}),
}))

const GitConfigSchema = z.object({
  enable_scopes:           z.boolean().default(false),
  enable_breaking_changes: z.boolean().default(true),
  enable_body:             z.boolean().default(true),
  scopes:                  z.array(z.string()).default(['api', 'auth', 'cli', 'config', 'core', 'db', 'deps', 'docs', 'test', 'ui']),
  description_guidelines:  z.array(z.string()).default([]),
  max_description_length:  z.number().int().default(72),
}).strict()

const WatchConfigSchema = z.object({
  enable: z.boolean().default(false),
}).strict()

const FilesConfigSchema = z.object({
  watch: WatchConfigSchema.optional(),
  ignore: z.array(z.string()).optional(),
}).strict().transform((data) => ({
  watch: WatchConfigSchema.parse(data.watch || {}),
  ignore: data.ignore ?? [
    '.byte/cache', '.ruff_cache', '.idea', '.venv', '.env',
    '.git', '.pytest_cache', '__pycache__', 'node_modules', 'dist',
  ],
}))

const LintCommandSchema = z.object({
  command:   z.array(z.string()),
  languages: z.array(z.string()),
})

const LintConfigSchema = z.object({
  enable:   z.boolean().default(false),
  commands: z.array(LintCommandSchema).default([]),
}).strict()

const PresetsConfigSchema = z.object({
  id:              z.string(),
  read_only_files: z.array(z.string()).default([]),
  editable_files:  z.array(z.string()).default([]),
  conventions:     z.array(z.string()).default([]),
  prompt:          z.string().nullable().default(null),
  load_on_boot:    z.boolean().default(false),
}).strict()

const EditFormatConfigSchema = z.object({
  enable_shell_commands: z.boolean().default(false),
  mask_message_count:    z.number().int().default(1),
}).strict()

export const ByteConfigSchema = z
  .object({
    version:     z.string().optional(),
    app:         AppConfigSchema.optional(),
    boot:        BootConfigSchema.optional(),
    cli:         CLIConfigSchema.optional(),
    edit_format: EditFormatConfigSchema.optional(),
    files:       FilesConfigSchema.optional(),
    git:         GitConfigSchema.optional(),
    lint:        LintConfigSchema.optional(),
    llm:         LLMConfigSchema.optional(),
    presets:     z.array(PresetsConfigSchema).optional(),
  })
  .passthrough()
  .transform((data) => {
    const { lsp: _lsp, mcp: _mcp, web: _web, system: _system, ...clean } = data as Record<string, unknown> & { lsp?: unknown; mcp?: unknown; web?: unknown; system?: unknown }
    return {
      version: (clean.version as string | undefined) ?? '0.0.0',
      app: AppConfigSchema.parse(clean.app || {}),
      boot: BootConfigSchema.parse(clean.boot || {}),
      cli: CLIConfigSchema.parse(clean.cli || {}),
      edit_format: EditFormatConfigSchema.parse(clean.edit_format || {}),
      files: FilesConfigSchema.parse(clean.files || {}),
      git: GitConfigSchema.parse(clean.git || {}),
      lint: LintConfigSchema.parse(clean.lint || {}),
      llm: LLMConfigSchema.parse(clean.llm || {}),
      presets: z.array(PresetsConfigSchema).parse((clean.presets as unknown[]) ?? []),
    }
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
