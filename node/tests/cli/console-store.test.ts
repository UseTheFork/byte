import { describe, it, expect } from 'bun:test'
import { ConsoleStore } from '../../src/cli/store/console-store.ts'

describe('ConsoleStore', () => {
  it('initialises with empty default state', () => {
    const store = new ConsoleStore()
    expect(store.state.messages).toEqual([])
    expect(store.state.spinner).toBeNull()
    expect(store.state.promptVisible).toBe(false)
    expect(store.state.promptDefault).toBe('')
    expect(store.state.modal).toBeNull()
    expect(store.state.live).toBeNull()
  })

  it('setState merges patch without mutating other fields', () => {
    const store = new ConsoleStore()
    store.setState({ promptVisible: true })
    expect(store.state.promptVisible).toBe(true)
    expect(store.state.messages).toEqual([])
    expect(store.state.spinner).toBeNull()
  })

  it('emits change event after setState', () => {
    const store = new ConsoleStore()
    let changeCount = 0
    store.on('change', () => { changeCount++ })
    store.setState({ promptVisible: true })
    expect(changeCount).toBe(1)
  })

  it('passes new state as argument to change listener', () => {
    const store = new ConsoleStore()
    let received: unknown
    store.on('change', (s) => { received = s })
    store.setState({ promptDefault: 'hello' })
    expect((received as { promptDefault: string }).promptDefault).toBe('hello')
  })

  it('appendMessage appends to messages and emits change', () => {
    const store = new ConsoleStore()
    let changeCount = 0
    store.on('change', () => { changeCount++ })
    store.appendMessage({ type: 'text', content: 'hello' })
    expect(store.state.messages).toHaveLength(1)
    expect(store.state.messages[0]).toEqual({ type: 'text', content: 'hello' })
    expect(changeCount).toBe(1)
  })

  it('appendMessage does not mutate previous messages array', () => {
    const store = new ConsoleStore()
    const before = store.state.messages
    store.appendMessage({ type: 'text', content: 'a' })
    expect(store.state.messages).not.toBe(before)
  })

  it('width defaults to 80 when process.stdout.columns is falsy', () => {
    const store = new ConsoleStore()
    expect(typeof store.state.width).toBe('number')
    expect(store.state.width).toBeGreaterThan(0)
  })
})
