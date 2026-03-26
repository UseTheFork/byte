import { describe, it, expect } from 'bun:test'
import { Service } from '../../src/support/service.ts'
import { ServiceProvider } from '../../src/support/service-provider.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const mockApp = {
  make: () => ({ on: () => {}, emit: async (p: unknown) => p }),
  singleton: () => {},
  bind: () => {},
  instance: () => {},
  running_unit_tests: () => false,
} as unknown as IApplication

describe('Service', () => {
  it('run() calls validate then handle', async () => {
    const order: string[] = []
    class TestService extends Service {
      override async validate() { order.push('validate'); return true }
      override async handle() { order.push('handle') }
    }
    const svc = new TestService(mockApp)
    await svc.run()
    expect(order).toEqual(['validate', 'handle'])
  })

  it('validate() returns true by default', async () => {
    class TestService extends Service {}
    const svc = new TestService(mockApp)
    expect(await svc.validate()).toBe(true)
  })
})

describe('ServiceProvider', () => {
  it('services() returns empty array by default', () => {
    class TestProvider extends ServiceProvider {}
    const p = new TestProvider(mockApp)
    expect(p.services()).toEqual([])
  })

  it('commands() returns empty array by default', () => {
    class TestProvider extends ServiceProvider {}
    const p = new TestProvider(mockApp)
    expect(p.commands()).toEqual([])
  })
})
