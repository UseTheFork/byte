import { describe, it, expect } from 'bun:test'
import { EventBus, EventType } from '../../src/foundation/event-bus.ts'
import { Payload } from '../../src/support/concerns/eventable.ts'
import type { IApplication } from '../../src/support/concerns/bootable.ts'

const mockApp = { make: () => ({ exception: () => {} }), singleton: () => {}, bind: () => {}, instance: () => {}, running_unit_tests: () => false } as unknown as IApplication

describe('EventType', () => {
  it('has string values', () => {
    expect(EventType.POST_BOOT).toBe('post_boot')
    expect(EventType.FILE_ADDED).toBe('file_added')
  })
})

describe('EventBus', () => {
  it('emits to registered listener', async () => {
    const bus = new EventBus(mockApp)
    const received: Payload[] = []
    bus.on(EventType.TEST, (p: Payload) => { received.push(p); return p })
    const payload = new Payload(EventType.TEST, { key: 'val' })
    await bus.emit(payload)
    expect(received.length).toBe(1)
    expect(received[0]!.get('key')).toBe('val')
  })

  it('returns payload unchanged when no listeners', async () => {
    const bus = new EventBus(mockApp)
    const payload = new Payload(EventType.TEST)
    const result = await bus.emit(payload)
    expect(result).toBe(payload)
  })

  it('chains multiple listeners sequentially', async () => {
    const bus = new EventBus(mockApp)
    const order: number[] = []
    bus.on(EventType.TEST, (p: Payload) => { order.push(1); return p })
    bus.on(EventType.TEST, async (p: Payload) => { order.push(2); return p })
    await bus.emit(new Payload(EventType.TEST))
    expect(order).toEqual([1, 2])
  })

  it('listener can transform payload', async () => {
    const bus = new EventBus(mockApp)
    bus.on(EventType.TEST, (p: Payload) => { p.set('added', true); return p })
    const result = await bus.emit(new Payload(EventType.TEST))
    expect(result.get('added')).toBe(true)
  })
})
