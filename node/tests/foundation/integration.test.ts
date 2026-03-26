import { describe, it, expect } from 'bun:test'
import { Application } from '../../src/foundation/application.ts'
import { FoundationServiceProvider } from '../../src/foundation/service-provider.ts'
import { ServiceProvider } from '../../src/support/service-provider.ts'
import { EventBus } from '../../src/foundation/event-bus.ts'
import { TaskManager } from '../../src/foundation/task-manager.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'
import path from 'path'

const testBasePath = path.resolve(process.cwd(), '..')

describe('Application + FoundationServiceProvider integration', () => {
  it('resolves EventBus after FoundationServiceProvider registers', () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const bus = app.make(EventBus as never) as EventBus
    expect(bus).toBeInstanceOf(EventBus)
  })

  it('event-bus string key resolves to EventBus', () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const bus = app.make<EventBus>('event-bus')
    expect(bus).toBeInstanceOf(EventBus)
  })

  it('TaskManager is available after registration', () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const tm = app.make(TaskManager as never) as TaskManager
    expect(tm).toBeInstanceOf(TaskManager)
  })

  it('EventBus emits and returns transformed payload', async () => {
    const app = Application.configure(testBasePath)
      .withProviders([FoundationServiceProvider as never])
      .create()
    const bus = app.make<EventBus>('event-bus')
    bus.on('test', (p: Payload) => { p.set('touched', true); return p })
    const result = await bus.emit(new Payload('test'))
    expect(result.get('touched')).toBe(true)
  })

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
})
