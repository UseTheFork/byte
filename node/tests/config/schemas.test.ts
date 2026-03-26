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
    expect(config.llm.weak_model.model).toBe('')
    expect(config.llm.main_model.provider).toBe('')
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
    expect(config.git.enable_breaking_changes).toBe(true)
  })

  it('unknown top-level keys are stripped silently', () => {
    const config = ByteConfigSchema.parse({ lsp: { enable: true }, mcp: { enable: true }, web: { enable: true }, system: { enable: true } })
    expect((config as Record<string, unknown>)['lsp']).toBeUndefined()
    expect((config as Record<string, unknown>)['mcp']).toBeUndefined()
    expect((config as Record<string, unknown>)['web']).toBeUndefined()
    expect((config as Record<string, unknown>)['system']).toBeUndefined()
  })
})
