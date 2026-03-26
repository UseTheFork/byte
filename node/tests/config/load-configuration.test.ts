import { describe, it, expect, mock } from 'bun:test'
import { ByteConfigException } from '../../src/config/exceptions.ts'
import type { ByteConfig } from '../../src/config/schemas.ts'

// Helper to build a minimal mock app
function makeApp(configPath = '/fake') {
  const instances: Record<string, unknown> = {}
  let detectedEnv = ''
  const app = {
    configPath: () => configPath,
    instance: (key: string, value: unknown) => { instances[key] = value },
    detectEnvironment: (cb: (a: unknown) => string) => { detectedEnv = cb(null); return detectedEnv },
  }
  return {
    app,
    instances,
    get detectedEnv() { return detectedEnv },
  }
}

describe('LoadConfiguration', () => {
  it('binds typed config to app and detects environment', async () => {
    mock.module('../../src/support/yaml.ts', () => ({
      Yaml: { loadAsDict: () => ({ app: { env: 'staging' } }) },
    }))
    const { LoadConfiguration } = await import('../../src/foundation/bootstrap/load-configuration.ts')
    const ctx = makeApp()
    const loader = new LoadConfiguration()
    loader.bootstrap(ctx.app as never)
    expect(ctx.instances['config']).toBeDefined()
    const config = ctx.instances['config'] as ByteConfig
    expect(config.app.env).toBe('staging')
    expect(ctx.detectedEnv).toBe('staging')
  })

  it('throws ByteConfigException on invalid config', async () => {
    mock.module('../../src/support/yaml.ts', () => ({
      Yaml: { loadAsDict: () => ({ cli: { ui_theme: 'invalid-theme' } }) },
    }))
    const { LoadConfiguration } = await import('../../src/foundation/bootstrap/load-configuration.ts')
    const ctx = makeApp()
    const loader = new LoadConfiguration()
    expect(() => loader.bootstrap(ctx.app as never)).toThrow(ByteConfigException)
  })

  it('boots with defaults when config.yaml absent', async () => {
    mock.module('../../src/support/yaml.ts', () => ({
      Yaml: { loadAsDict: () => ({}) },
    }))
    const { LoadConfiguration } = await import('../../src/foundation/bootstrap/load-configuration.ts')
    const ctx = makeApp()
    const loader = new LoadConfiguration()
    loader.bootstrap(ctx.app as never)
    const config = ctx.instances['config'] as ByteConfig
    expect(config.app.env).toBe('production')
    expect(config.git.max_description_length).toBe(72)
    expect(config.presets).toEqual([])
  })
})
