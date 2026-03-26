import { describe, it, expect } from 'bun:test'
import { Application } from '../../src/foundation/application.ts'
import path from 'path'

const testBasePath = path.resolve(process.cwd(), '..')

describe('Application', () => {
  it('create() returns an Application instance', () => {
    const app = Application.configure(testBasePath).create()
    expect(app).toBeInstanceOf(Application)
  })

  it('rootPath() returns a string path', () => {
    const app = Application.configure(testBasePath).create()
    expect(typeof app.rootPath()).toBe('string')
  })

  it('configPath() returns path ending in .byte', () => {
    const app = Application.configure(testBasePath).create()
    expect(app.configPath()).toContain('.byte')
  })

  it('instance() and make() round-trip', () => {
    const app = Application.configure(testBasePath).create()
    app.instance('test-key', 'hello')
    expect(app.make('test-key')).toBe('hello')
  })

  it('is not booted initially', () => {
    const app = Application.configure(testBasePath).create()
    expect(app.isBooted()).toBe(false)
  })

  it('isDevelopment() works after env is set', () => {
    const app = Application.configure(testBasePath).create()
    app.instance('env', 'development')
    expect(app.isDevelopment()).toBe(true)
  })
})
