import { describe, it, expect } from 'bun:test'
import { Bootable, type IApplication } from '../../src/support/concerns/bootable.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'
import { Configurable } from '../../src/support/concerns/configurable.ts'
import { Conditionable } from '../../src/support/concerns/conditionable.ts'
import { ArrayStore } from '../../src/support/array-store.ts'

const mockApp = {} as IApplication

describe('Bootable', () => {
  it('boot() is called once via ensureBooted()', () => {
    let callCount = 0
    class MyService extends Bootable {
      override boot() { callCount++ }
    }
    const svc = new MyService(mockApp)
    svc.ensureBooted()
    svc.ensureBooted() // second call should be no-op
    expect(callCount).toBe(1)
  })

  it('bootConcerns() is called before boot()', () => {
    const order: string[] = []
    class MyService extends Bootable {
      protected override bootConcerns() { order.push('concerns') }
      override boot() { order.push('boot') }
    }
    new MyService(mockApp).ensureBooted()
    expect(order).toEqual(['concerns', 'boot'])
  })
})

describe('Payload', () => {
  it('wraps data in ArrayStore', () => {
    const p = new Payload('test_event', { key: 'val' })
    expect(p.get('key')).toBe('val')
  })

  it('accepts ArrayStore directly', () => {
    const store = new ArrayStore<string>({ x: 'y' })
    const p = new Payload('test_event', store as ArrayStore<unknown>)
    expect(p.get('x')).toBe('y')
  })

  it('set returns self for chaining', () => {
    const p = new Payload('test')
    const result = p.set('a', 1)
    expect(result).toBe(p)
    expect(p.get('a')).toBe(1)
  })

  it('update merges multiple keys', () => {
    const p = new Payload('test')
    p.update({ a: 1, b: 2 })
    expect(p.get('a')).toBe(1)
    expect(p.get('b')).toBe(2)
  })
})

describe('Configurable', () => {
  it('config() returns an ArrayStore', () => {
    class MyService extends Configurable {}
    const svc = new MyService()
    expect(svc.config()).toBeInstanceOf(ArrayStore)
  })

  it('config persists across calls', () => {
    class MyService extends Configurable {}
    const svc = new MyService()
    svc.config().add('key', 'val')
    expect(svc.config().get('key')).toBe('val')
  })
})

describe('Conditionable', () => {
  it('when executes callback when condition truthy', () => {
    let called = false
    class MyObj extends Conditionable {}
    new MyObj().when(true, () => { called = true })
    expect(called).toBe(true)
  })

  it('when skips callback when condition falsy', () => {
    let called = false
    class MyObj extends Conditionable {}
    new MyObj().when(false, () => { called = true })
    expect(called).toBe(false)
  })

  it('unless executes callback when condition falsy', () => {
    let called = false
    class MyObj extends Conditionable {}
    new MyObj().unless(false, () => { called = true })
    expect(called).toBe(true)
  })

  it('when returns self for chaining', () => {
    class MyObj extends Conditionable {}
    const obj = new MyObj()
    expect(obj.when(true, () => {})).toBe(obj)
  })
})
