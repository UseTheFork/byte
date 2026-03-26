import { describe, it, expect } from 'bun:test'
import { Container } from '../../src/foundation/container.ts'

class ServiceA {
  static token = Symbol('ServiceA')
  value = 'a'
}
class ServiceB {
  static token = Symbol('ServiceB')
  constructor(public dep: ServiceA) {}
}

describe('Container', () => {
  it('instance() stores and make() retrieves by string key', () => {
    const c = new Container()
    c.instance('app', { name: 'byte' })
    expect(c.make<{ name: string }>('app').name).toBe('byte')
  })

  it('singleton() creates once, caches', () => {
    const c = new Container()
    let count = 0
    c.singleton(ServiceA, () => { count++; return new ServiceA() })
    c.make(ServiceA)
    c.make(ServiceA)
    expect(count).toBe(1)
  })

  it('bind() creates new instance each time', () => {
    const c = new Container()
    c.bind(ServiceA, () => new ServiceA())
    const a1 = c.make(ServiceA)
    const a2 = c.make(ServiceA)
    expect(a1).not.toBe(a2)
  })

  it('bound() returns true when registered', () => {
    const c = new Container()
    c.instance('env', 'testing')
    expect(c.bound('env')).toBe(true)
    expect(c.bound('missing')).toBe(false)
  })

  it('flush() clears all state', () => {
    const c = new Container()
    c.instance('env', 'test')
    c.flush()
    expect(c.bound('env')).toBe(false)
  })

  it('make() by class uses token as key', () => {
    const c = new Container()
    const instance = new ServiceA()
    c.instance(ServiceA, instance)
    expect(c.make(ServiceA)).toBe(instance)
  })

  it('get() and set() work like make/instance', () => {
    const c = new Container()
    c.set('key', 'value')
    expect(c.get('key')).toBe('value')
  })
})
